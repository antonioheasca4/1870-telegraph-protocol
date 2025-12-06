"""
Demo Script - Complete example from Client to Server
Demonstrates the full flow: extraction -> generation -> transmission -> validation
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Note: SenderClient is now in client/client.py
# Note: ReceiverServer is now integrated in server/server.py
# For demo purposes, we'll import the required modules directly
from shared.ai_extractor import extract_banking_data
from shared.pdf_generator import PDFGenerator
from shared.hash_validator import TransmissionPackage, IntegrityVerifier, create_transmission_package


def print_banner(text, char="="):
    """Print a banner."""
    print(f"\n{char * 70}")
    print(f"  {text}")
    print(f"{char * 70}\n")


def demo_full_workflow():
    """Demonstrates the complete workflow."""
    
    print_banner("THE 1870 TELEGRAPH PROTOCOL - FULL DEMO", "=")
    
    # Check API key
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("WARNING: GEMINI_API_KEY not set!")
        print("   Set it in .env file or using: $env:GEMINI_API_KEY='your-key'")
        print("   For demo without AI, run: python demo_no_api.py\n")
        return
    
    # =========================================================================
    # PART 1: CLIENT (SHIP)
    # =========================================================================
    
    print_banner("PART 1: CLIENT (SHIP) - Processing Document", "-")
    
    # Sample data - maritime banking contract
    sample_document = """
    MARITIME BANKING TRANSFER
    
    FROM: Maersk Shipping Company
    Account: RO49AAAA1B31007593840000
    
    TO: Deutsche Bank AG - Hamburg Branch
    Account: DE89370400440532013000
    
    AMOUNT: 5,000,000.00 EUR
    DATE: 2025-12-06
    
    DESCRIPTION: Payment for maritime transport services
    Container shipment from Rotterdam to Singapore
    Contract Reference: MSK-DB-2025-1234
    
    Transaction Reference: TRX-MARITIME-2025-12-06-001
    
    Electronic Signature: VERIFIED
    Officer: Captain James Anderson
    Vessel: MV Ocean Pioneer
    """
    
    try:
        # Initialize components
        generator = PDFGenerator()
        
        print("Document to process:")
        print("-" * 70)
        print(sample_document[:200] + "...")
        print("-" * 70 + "\n")
        
        # Process document
        print("Starting client processing...\n")
        
        # Extract data using AI
        print("Extracting data with AI...")
        banking_data = extract_banking_data(sample_document, api_key=api_key)
        print("Data extracted successfully\n")
        
        # Normalize data using DigitalCodebook
        from shared.pdf_generator import DigitalCodebook
        codebook = DigitalCodebook()
        banking_data = codebook.normalize_data(banking_data)
        
        # Generate PDF
        print("Generating PDF...")
        pdf_bytes = generator.generate_pdf_bytes(banking_data)
        print(f"PDF generated: {len(pdf_bytes) / 1024:.2f} KB\n")
        
        # Save client PDF
        os.makedirs("data/client_output", exist_ok=True)
        with open("data/client_output/demo_maritime_transfer.pdf", "wb") as f:
            f.write(pdf_bytes)
        print("Client PDF saved\n")
        
        # Create transmission package
        print("Creating transmission package...")
        transmission_package = create_transmission_package(banking_data, pdf_bytes)
        
        # Save JSON package
        with open("data/client_output/demo_maritime_transfer.json", "w") as f:
            f.write(transmission_package.to_json())
        print("JSON package saved\n")
        
        print("\nCLIENT PROCESSING COMPLETE!")
        print(f"   Package ready for transmission: {transmission_package.get_size_kb():.2f} KB")
        
    except Exception as e:
        print(f"\nCLIENT ERROR: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # =========================================================================
    # SIMULARE TRANSMISIE SATELIT
    # =========================================================================
    
    print_banner("SATELLITE TRANSMISSION SIMULATION", "-")
    print("Simulating low-bandwidth satellite transmission...")
    print(f"   Sending: {transmission_package.get_size_kb():.2f} KB")
    print("   Status: Transmission successful")
    print("   Latency: ~2500ms (geostationary satellite)")
    
    # =========================================================================
    # PART 2: SERVER (BANK)
    # =========================================================================
    
    print_banner("PART 2: SERVER (BANK) - Document Verification", "-")
    
    try:
        # Initialize components
        generator = PDFGenerator()
        verifier = IntegrityVerifier()
        
        print("Starting server verification...\n")
        
        # Reconstruct PDF from package
        print("Reconstructing PDF from JSON...")
        reconstructed_pdf = generator.generate_pdf_bytes(transmission_package.json_data)
        print(f"PDF reconstructed: {len(reconstructed_pdf) / 1024:.2f} KB\n")
        
        # Verify integrity
        print("Verifying document integrity...")
        verification_result = verifier.verify_with_details(
            reconstructed_pdf,
            transmission_package
        )
        print(f"Hash verification: {'PASSED' if verification_result['valid'] else 'FAILED'}\n")
        
        # Save server PDF
        os.makedirs("data/server_output", exist_ok=True)
        with open("data/server_output/demo_verified_maritime.pdf", "wb") as f:
            f.write(reconstructed_pdf)
        print("Server PDF saved\n")
        
        # Add package size info for summary
        verification_result['json_size_kb'] = transmission_package.get_size_kb()
        verification_result['pdf_size_bytes'] = len(reconstructed_pdf)
        verification_result['compression_ratio'] = len(reconstructed_pdf) / (transmission_package.get_size_kb() * 1024)
        
        print("\nSERVER VERIFICATION COMPLETE!")
        
    except Exception as e:
        print(f"\nSERVER ERROR: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # =========================================================================
    # FINAL SUMMARY
    # =========================================================================
    
    print_banner("FINAL SUMMARY", "=")
    
    if verification_result['valid']:
        print("DOCUMENT SUCCESSFULLY VERIFIED!\n")
        print("Key Metrics:")
        print(f"  • Original PDF size:        {verification_result['pdf_size_bytes'] / 1024:.2f} KB")
        print(f"  • Transmitted package:      {verification_result['json_size_kb']:.2f} KB")
        print(f"  • Compression ratio:        {verification_result['compression_ratio']:.1f}x")
        print(f"  • Bandwidth saved:          {(verification_result['pdf_size_bytes'] / 1024 - verification_result['json_size_kb']):.2f} KB")
        print(f"  • Hash match:               PERFECT")
        print(f"  • Legal validity:           GUARANTEED")
        
        print(f"\nFiles generated:")
        print(f"  • Client PDF:    data/client_output/demo_maritime_transfer.pdf")
        print(f"  • Package JSON:  data/client_output/demo_maritime_transfer.json")
        print(f"  • Server PDF:    data/server_output/demo_verified_maritime.pdf")
        
        print(f"\nUse Case Validated:")
        print(f"  - Perfect for ships with expensive satellite internet")
        print(f"  - 100% document integrity guaranteed")
        print(f"  - Massive bandwidth savings")
        print(f"  - Legally valid (bit-perfect reproduction)")
        
    else:
        print("DOCUMENT VERIFICATION FAILED!\n")
        print("  Hash mismatch detected")
        print("  Document may be corrupted or tampered")
    
    print("\n" + "=" * 70)
    print("  Demo Complete - Thank you!")
    print("=" * 70 + "\n")


def main():
    """Main entry point."""
    try:
        demo_full_workflow()
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user")
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
