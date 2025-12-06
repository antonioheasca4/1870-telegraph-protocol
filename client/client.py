"""
Web Client - Flask server for AI-powered document processing
Accepts file uploads or text, uses AI to extract banking data.
"""

import sys
import os
import socket
import json
import webbrowser
import base64
from pathlib import Path
from datetime import datetime, timezone
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from shared.pdf_generator import DigitalCodebook
from shared.hash_validator import create_transmission_package
from shared.ai_extractor import extract_banking_data

app = Flask(__name__)
CORS(app)

# Configuration
SERVER_HOST = "localhost"
SERVER_PORT = 8870
OUTPUT_DIR = Path(__file__).parent.parent / "data" / "client_output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

codebook = DigitalCodebook()


def generate_signature():
    """Generate automatic signature with timestamp."""
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    return f"Electronically verified - {timestamp}"


def generate_reference_number(transaction_type: str):
    """Generate automatic reference number."""
    now = datetime.now(timezone.utc)
    date_str = now.strftime("%Y%m%d")
    time_str = now.strftime("%H%M%S")
    return f"{transaction_type.upper()}-{date_str}-{time_str}"


def send_to_server(transmission_package) -> dict:
    """
    Send package to TCP server.
    
    Args:
        transmission_package: Package to send
        
    Returns:
        Server response
    """
    try:
        # Create socket connection
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.settimeout(10)
        
        client_socket.connect((SERVER_HOST, SERVER_PORT))
        
        # Serialize package
        package_json = transmission_package.to_json()
        package_bytes = package_json.encode('utf-8')
        
        # Send data size first
        client_socket.sendall(len(package_bytes).to_bytes(4, 'big'))
        
        # Send actual data
        client_socket.sendall(package_bytes)
        
        # Receive response size
        response_size_data = client_socket.recv(4)
        response_size = int.from_bytes(response_size_data, 'big')
        
        # Receive response
        response_data = b""
        while len(response_data) < response_size:
            chunk = client_socket.recv(min(4096, response_size - len(response_data)))
            if not chunk:
                break
            response_data += chunk
        
        response = json.loads(response_data.decode('utf-8'))
        client_socket.close()
        
        return response
        
    except ConnectionRefusedError:
        raise Exception("Server not running. Start with: python server/server_listener.py")
    except Exception as e:
        raise Exception(f"Transmission error: {str(e)}")


@app.route('/')
def index():
    """Serve the web interface."""
    html_path = Path(__file__).parent / "web_interface.html"
    return send_file(html_path)


@app.route('/submit_transfer', methods=['POST'])
def submit_transfer():
    """Handle document upload and AI extraction."""
    try:
        # Check for API key
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            return jsonify({
                'status': 'error',
                'error': 'GEMINI_API_KEY not configured. Please set it in .env file.'
            }), 500
        
        # Get uploaded file or text
        document_file = request.files.get('document_file')
        document_text = request.form.get('document_text')
        
        if not document_file and not document_text:
            return jsonify({
                'status': 'error',
                'error': 'Please provide either a document file or text.'
            }), 400
        
        # Extract data using AI
        if document_file:
            # Save temporary file
            temp_path = OUTPUT_DIR / f"temp_{document_file.filename}"
            document_file.save(temp_path)
            
            try:
                # Extract from file
                extracted_data = extract_banking_data(str(temp_path), api_key=api_key)
            finally:
                # Clean up temp file
                if temp_path.exists():
                    temp_path.unlink()
        else:
            # Extract from text
            extracted_data = extract_banking_data(document_text, api_key=api_key)
        
        # Normalize data using DigitalCodebook
        transfer_data = codebook.normalize_data(extracted_data)
        
        # Generate automatic fields
        current_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        reference_number = generate_reference_number(transfer_data.get('transaction_type', 'transfer'))
        signature = generate_signature()
        
        # Update with auto-generated fields
        transfer_data['date'] = current_date
        transfer_data['reference_number'] = reference_number
        transfer_data['signature_status'] = 'verified'
        if not transfer_data.get('additional_info'):
            transfer_data['additional_info'] = signature
        
        # Generate PDF
        pdf_bytes = codebook.reconstruct_document(transfer_data)
        
        # Save PDF
        pdf_path = OUTPUT_DIR / f"{reference_number}.pdf"
        with open(pdf_path, 'wb') as f:
            f.write(pdf_bytes)
        
        # Create transmission package
        transmission_package = create_transmission_package(transfer_data, pdf_bytes)
        
        # Save package
        package_path = OUTPUT_DIR / f"{reference_number}.json"
        transmission_package.save_to_file(str(package_path))
        
        # Send to server
        server_response = send_to_server(transmission_package)
        
        # Return success response
        return jsonify({
            'status': 'success',
            'reference_number': reference_number,
            'hash': transmission_package.document_hash,
            'package_size_kb': round(transmission_package.get_size_kb(), 2),
            'pdf_size_kb': round(len(pdf_bytes) / 1024, 2),
            'server_response': server_response,
            'extracted_data': extracted_data,  # Include extracted data in response
            'files': {
                'pdf': str(pdf_path),
                'package': str(package_path)
            }
        })
        
    except ValueError as e:
        # User-friendly validation errors (e.g., no banking data found)
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 400
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500


def main():
    """Main entry point."""
    print("\n" + "=" * 70)
    print(" 1870 TELEGRAPH PROTOCOL - WEB CLIENT")
    print("=" * 70)
    print(f"Web Interface: http://localhost:5870")
    print(f"Backend Server: {SERVER_HOST}:{SERVER_PORT}")
    print("=" * 70)
    print("\n  IMPORTANT: Make sure the server is running!")
    print("   Start server: python server/server_listener.py")
    print("\n Opening web browser...")
    print("=" * 70 + "\n")
    
    # Open browser
    webbrowser.open('http://localhost:5870')
    
    # Start Flask
    app.run(host='0.0.0.0', port=5870, debug=False)


if __name__ == "__main__":
    main()
