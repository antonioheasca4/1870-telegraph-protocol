"""
Server Listener - Continuous listening server
Listens for incoming packages from clients and processes them automatically.
"""

import sys
import socket
import json
import threading
from pathlib import Path
from typing import Optional, Dict, Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from shared.pdf_generator import DigitalCodebook
from shared.hash_validator import TransmissionPackage, IntegrityVerifier


class ReceiverServer:
    """
    Server for bank - receives compressed packages and reconstructs documents.
    """
    
    def __init__(self):
        """
        Initializes receiver server.
        """
        self.codebook = DigitalCodebook()
        
        # Output directory
        self.output_dir = Path(__file__).parent.parent / "data" / "server_output"
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def receive_and_verify(
        self,
        transmission_package: TransmissionPackage,
        output_name: Optional[str] = None,
        save_pdf: bool = True
    ) -> Dict[str, Any]:
        """
        Receives package, reconstructs document and validates integrity.
        
        Steps:
        1. Receive package (JSON + hash)
        2. Reconstruct PDF using same codebook
        3. Calculate hash of reconstructed PDF
        4. Compare with received hash - VALIDATION
        
        Args:
            transmission_package: Package with JSON data and hash
            output_name: Name for output file
            save_pdf: Whether to save reconstructed PDF
            
        Returns:
            Dict with verification results
        """
        print(" RECEIVER SERVER (BANCA) - Document Verification")
        print("=" * 70)
        
        # STEP 1: Package reception
        print("\n[STEP 1]  Receiving Transmission Package...")
        package_size_kb = transmission_package.get_size_kb()
        print(f"   Package received: {package_size_kb:.2f} KB")
        print(f"  Expected hash: {transmission_package.document_hash[:16]}...")
        print(f"  Transaction type: {transmission_package.json_data.get('transaction_type', 'N/A')}")
        
        # STEP 2: Deterministic PDF reconstruction
        print("\n[STEP 2]  Reconstructing PDF from JSON...")
        print("  Using Digital Codebook (same as sender)")
        
        reconstructed_pdf_bytes = self.codebook.reconstruct_document(
            transmission_package.json_data
        )
        
        pdf_size_kb = len(reconstructed_pdf_bytes) / 1024
        print(f"   PDF reconstructed: {pdf_size_kb:.2f} KB")
        
        # STEP 3: Integrity verification
        print("\n[STEP 3]  Integrity Verification...")
        print("  Calculating hash of reconstructed PDF...")
        
        is_valid, message = IntegrityVerifier.verify_reconstruction(
            reconstructed_pdf_bytes,
            transmission_package
        )
        
        verification_result = IntegrityVerifier.verify_with_details(
            reconstructed_pdf_bytes,
            transmission_package
        )
        
        print(f"  Received hash:  {transmission_package.document_hash[:32]}...")
        print(f"  Computed hash:  {verification_result['actual_hash'][:32]}...")
        
        if is_valid:
            print(f"\n   {message}")
            print("  Document is AUTHENTIC and UNALTERED")
            print("  PDF matches bit-for-bit with sender's version")
        else:
            print(f"\n   {verification_result['message']}")
            print("  WARNING: Document may be corrupted or tampered!")
        
        # Save reconstructed PDF
        if save_pdf:
            if output_name is None:
                ref = transmission_package.json_data.get('reference_number', 'received')
                output_name = f"verified_{ref}"
            
            pdf_path = self.output_dir / f"{output_name}.pdf"
            with open(pdf_path, 'wb') as f:
                f.write(reconstructed_pdf_bytes)
            print(f"\n   PDF saved: {pdf_path}")
        
        # STEP 4: Statistics
        print("\n[STEP 4]  Transmission Statistics")
        print(f"  Original PDF size: {pdf_size_kb:.2f} KB")
        print(f"  Transmitted package: {package_size_kb:.2f} KB")
        print(f"  Compression ratio: {verification_result['compression_ratio']:.1f}x")
        bandwidth_saved = pdf_size_kb - package_size_kb
        print(f"  Bandwidth saved: {bandwidth_saved:.2f} KB")
        
        print(f"\n Document verification complete!")
        print("=" * 70)
        
        return verification_result


class ServerListener:
    """
    TCP Server that listens for client connections and processes packages.
    """
    
    def __init__(self, host: str = "localhost", port: int = 8870):
        """
        Initialize server listener.
        
        Args:
            host: Host address to bind to
            port: Port number (8870 = 1870 Telegraph Protocol)
        """
        self.host = host
        self.port = port
        self.server = ReceiverServer()
        self.running = False
        
    def handle_client(self, client_socket: socket.socket, address: tuple):
        """
        Handle incoming client connection.
        
        Args:
            client_socket: Client socket connection
            address: Client address (host, port)
        """
        try:
            print(f"\n{'=' * 70}")
            print(f" New connection from: {address[0]}:{address[1]}")
            print(f"{'=' * 70}")
            
            # Receive data size first (4 bytes)
            size_data = client_socket.recv(4)
            if not size_data:
                print(" No data received")
                return
                
            data_size = int.from_bytes(size_data, 'big')
            print(f" Expecting {data_size} bytes...")
            
            # Receive actual data
            received_data = b""
            while len(received_data) < data_size:
                chunk = client_socket.recv(min(4096, data_size - len(received_data)))
                if not chunk:
                    break
                received_data += chunk
            
            print(f" Received {len(received_data)} bytes")
            
            # Parse JSON package
            package_data = json.loads(received_data.decode('utf-8'))
            transmission_package = TransmissionPackage.from_dict(package_data)
            
            # Process package
            print("\n Processing package...")
            result = self.server.receive_and_verify(
                transmission_package,
                output_name=f"received_{transmission_package.json_data.get('reference_number', 'unknown')}",
                save_pdf=True  # Save reconstructed PDF on server
            )
            
            # Send response
            response = {
                "status": "success" if result['valid'] else "error",
                "valid": result['valid'],
                "message": "Document verified and accepted" if result['valid'] else "Hash verification failed",
                "hash": result['actual_hash']
            }
            
            response_json = json.dumps(response).encode('utf-8')
            client_socket.sendall(len(response_json).to_bytes(4, 'big'))
            client_socket.sendall(response_json)
            
            print(f"\n Response sent to client")
            
        except Exception as e:
            print(f"\n Error handling client: {e}")
            import traceback
            traceback.print_exc()
            
            # Send error response
            try:
                error_response = {
                    "status": "error",
                    "valid": False,
                    "message": str(e)
                }
                response_json = json.dumps(error_response).encode('utf-8')
                client_socket.sendall(len(response_json).to_bytes(4, 'big'))
                client_socket.sendall(response_json)
            except:
                pass
        finally:
            client_socket.close()
            print(f"{'=' * 70}\n")
    
    def start(self):
        """
        Start the server and listen for connections.
        """
        self.running = True
        
        # Create socket
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.settimeout(1.0)  # Set timeout to allow KeyboardInterrupt
        
        try:
            server_socket.bind((self.host, self.port))
            server_socket.listen(5)
            
            print("\n" + "=" * 70)
            print(" 1870 TELEGRAPH PROTOCOL - SERVER LISTENER")
            print("=" * 70)
            print(f" Server listening on {self.host}:{self.port}")
            print(f"⏳ Waiting for client connections...")
            print(f" Press Ctrl+C to stop server")
            print("=" * 70 + "\n")
            
            while self.running:
                try:
                    # Accept client connection (will timeout every second)
                    client_socket, address = server_socket.accept()
                    
                    # Handle client in separate thread
                    client_thread = threading.Thread(
                        target=self.handle_client,
                        args=(client_socket, address)
                    )
                    client_thread.daemon = True
                    client_thread.start()
                    
                except socket.timeout:
                    # Timeout is normal, allows checking for KeyboardInterrupt
                    continue
                except KeyboardInterrupt:
                    print("\n\n  Server shutdown requested...")
                    break
                except Exception as e:
                    if self.running:
                        print(f" Error accepting connection: {e}")
                        
        finally:
            self.running = False
            server_socket.close()
            print("\n Server stopped\n")


def main():
    """Main entry point."""
    server = ServerListener(host="localhost", port=8870)
    
    try:
        server.start()
    except KeyboardInterrupt:
        print("\n\n  Server interrupted by user")
    except Exception as e:
        print(f"\n\n Server error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
