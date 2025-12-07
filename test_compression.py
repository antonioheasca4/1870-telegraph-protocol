"""
Semantic Compression Test: Maritime Banking Examples

This script tests semantic compression (JSON + hash) on maritime banking documents
and saves results for inspection.
"""

import os
import json
import argparse
from pathlib import Path
from shared.ai_extractor import AIExtractor
from shared.pdf_generator import DigitalCodebook
from shared.hash_validator import create_transmission_package


def test_compression_methods(file_path: str, example_type: str = "test"):
    """
    Test semantic compression on a maritime banking document.
    
    Args:
        file_path: Path to the document to test
        example_type: Type of example (swift/wire/payment) for naming output files
    """
    print("=" * 80)
    print("SEMANTIC COMPRESSION TEST")
    print("=" * 80)
    
    # Create test output directory
    test_dir = Path("test")
    test_dir.mkdir(exist_ok=True)
    
    # Read original file
    with open(file_path, 'rb') as f:
        original_bytes = f.read()
    
    original_size = len(original_bytes)
    print(f"\n📄 Original File: {Path(file_path).name}")
    print(f"   Size: {original_size:,} bytes ({original_size / 1024:.2f} KB)")
    
    # Test semantic compression
    print("\n" + "=" * 80)
    print("SEMANTIC COMPRESSION (1870 Telegraph Protocol)")
    print("=" * 80)
    
    # Load API key
    from dotenv import load_dotenv
    load_dotenv()
    api_key = os.getenv('GEMINI_API_KEY')
    
    if not api_key:
        print("\n❌ GEMINI_API_KEY not found. Skipping AI extraction.")
        print("   (Set API key to test semantic compression)")
        return
    
    try:
        # Extract with AI
        print("\n🔍 Extracting data with Google Gemini AI...")
        extractor = AIExtractor(api_key=api_key)
        extracted_data = extractor.extract_from_file(file_path)
        
        # Create transmission package with field compression
        codebook = DigitalCodebook()
        normalized_data = codebook.normalize_data(extracted_data)
        
        # Compress field names for transmission
        compressed_data = codebook.compress_fields(normalized_data)
        
        # Generate PDF from normalized (full) data
        pdf_bytes = codebook.reconstruct_document(normalized_data)
        
        # Create package with COMPRESSED data
        package = create_transmission_package(compressed_data, pdf_bytes)
        
        # Get package size with compression
        package_json = json.dumps(package.to_dict(), ensure_ascii=False)
        semantic_size = len(package_json.encode('utf-8'))
        
        # Calculate size without compression for comparison
        package_uncompressed = create_transmission_package(normalized_data, pdf_bytes)
        uncompressed_json = json.dumps(package_uncompressed.to_dict(), ensure_ascii=False)
        uncompressed_size = len(uncompressed_json.encode('utf-8'))
        
        print(f"\n📦 Semantic Compression Results:")
        print(f"   Package size (compressed): {semantic_size:,} bytes ({semantic_size / 1024:.2f} KB)")
        print(f"   Package size (uncompressed): {uncompressed_size:,} bytes ({uncompressed_size / 1024:.2f} KB)")
        print(f"   Field compression gain: {((uncompressed_size - semantic_size) / uncompressed_size * 100):.1f}%")
        print(f"   Overall compression ratio: {original_size / semantic_size:.2f}x")
        print(f"   Total bandwidth savings: {((original_size - semantic_size) / original_size * 100):.1f}%")
        
        # Save results to test/ folder
        print(f"\n💾 Saving results to test/ folder...")
        
        # 1. Save JSON package (client-side transmission)
        json_path = test_dir / f"{example_type}_transmission.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(package.to_dict(), f, ensure_ascii=False, indent=2)
        print(f"   ✓ Client JSON: {json_path} ({semantic_size:,} bytes)")
        
        # 2. Save client-reconstructed PDF
        client_pdf_path = test_dir / f"{example_type}_client_reconstructed.pdf"
        with open(client_pdf_path, 'wb') as f:
            f.write(pdf_bytes)
        client_pdf_size = len(pdf_bytes)
        print(f"   ✓ Client PDF: {client_pdf_path} ({client_pdf_size:,} bytes)")
        
        # 3. Simulate server-side reconstruction
        server_codebook = DigitalCodebook()
        server_pdf_bytes = server_codebook.reconstruct_document(normalized_data)
        server_pdf_path = test_dir / f"{example_type}_server_reconstructed.pdf"
        with open(server_pdf_path, 'wb') as f:
            f.write(server_pdf_bytes)
        server_pdf_size = len(server_pdf_bytes)
        print(f"   ✓ Server PDF: {server_pdf_path} ({server_pdf_size:,} bytes)")
        
        # Verify deterministic reconstruction
        if pdf_bytes == server_pdf_bytes:
            print(f"   ✓ Deterministic: Client PDF == Server PDF (bit-perfect reconstruction)")
        else:
            print(f"   ⚠ Warning: Client and Server PDFs differ!")
        
        # Summary
        print("\n" + "=" * 80)
        print("COMPRESSION SUMMARY")
        print("=" * 80)
        
        print(f"\n📊 Results:")
        print(f"   Original document:    {original_size:,} bytes ({original_size / 1024:.2f} KB)")
        print(f"   Transmitted package:  {semantic_size:,} bytes ({semantic_size / 1024:.2f} KB)")
        print(f"   Reconstructed PDF:    {client_pdf_size:,} bytes ({client_pdf_size / 1024:.2f} KB)")
        print(f"\n   Compression ratio:    {original_size / semantic_size:.2f}x")
        print(f"   Bandwidth saved:      {original_size - semantic_size:,} bytes ({(original_size - semantic_size) / 1024:.2f} KB)")
        print(f"   Savings percentage:   {((original_size - semantic_size) / original_size * 100):.1f}%")
        
        # Protocol benefits
        print("\n" + "=" * 80)
        print("PROTOCOL BENEFITS")
        print("=" * 80)
        
        print("\n✅ Semantic Compression Advantages:")
        print("   1. 🎯 Deterministic reconstruction (same JSON = same PDF, bit-perfect)")
        print("   2. ⚡ No decompression needed on server (instant access)")
        print("   3. 🔒 Cryptographic integrity validation (SHA-256 hash)")
        print("   4. 📋 Structured data for processing/automation")
        print("   5. 🔍 Searchable and queryable without reconstruction")
        print("   6. 🌊 Optimized for maritime/satellite bandwidth scenarios")
        
        print("\n💰 Cost Savings (Satellite @ $10/MB):")
        saved_mb = (original_size - semantic_size) / (1024 * 1024)
        saved_cost = saved_mb * 10
        print(f"   Bandwidth saved: {saved_mb:.4f} MB")
        print(f"   Cost saved per transmission: ${saved_cost:.2f} USD")
        
    except Exception as e:
        print(f"\n❌ Error during semantic compression test: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Run compression tests on maritime banking examples."""
    # Setup argument parser
    parser = argparse.ArgumentParser(
        description='Test semantic compression on maritime banking examples',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python test_compression.py --example swift    # Test SWIFT port charges
  python test_compression.py --example wire     # Test WIRE emergency fuel
  python test_compression.py --example payment  # Test PAYMENT cargo handling
  python test_compression.py --example all      # Test all examples
        """
    )
    parser.add_argument(
        '--example',
        choices=['swift', 'wire', 'payment', 'all'],
        default='swift',
        help='Which maritime example to test (default: swift)'
    )
    
    args = parser.parse_args()
    
    # Map example types to file paths
    example_files = {
        'swift': 'examples/example_swift.txt',
        'wire': 'examples/example_wire_urgent.txt',
        'payment': 'examples/example_payment_cargo.txt'
    }
    
    # Determine which files to test
    if args.example == 'all':
        files_to_test = example_files.items()
    else:
        files_to_test = [(args.example, example_files[args.example])]
    
    # Run tests
    for example_type, test_file in files_to_test:
        if not os.path.exists(test_file):
            print(f"\n❌ Error: {test_file} not found")
            print(f"   Please ensure the {example_type.upper()} example exists")
            continue
        
        print(f"\n{'='*80}")
        print(f"TESTING: {example_type.upper()} MARITIME BANKING EXAMPLE")
        print(f"{'='*80}\n")
        
        test_compression_methods(test_file, example_type)
    
    print("\n" + "=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()
