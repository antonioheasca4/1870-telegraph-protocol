"""
Hash Validator Module
Ensures document integrity through SHA-256 hash.
Allows validation that reconstructed document on server is identical to client.
"""

import hashlib
import json
from typing import Dict, Any, Tuple


class HashValidator:
    """Calculates and validates SHA-256 hashes for documents."""
    
    @staticmethod
    def calculate_hash(data: bytes) -> str:
        """
        Calculates SHA-256 hash for binary data.
        
        Args:
            data: Binary data (e.g. PDF bytes)
            
        Returns:
            SHA-256 hash as hexadecimal string
        """
        sha256_hash = hashlib.sha256()
        sha256_hash.update(data)
        return sha256_hash.hexdigest()
    
    @staticmethod
    def calculate_hash_from_file(file_path: str) -> str:
        """
        Calculates SHA-256 hash for a file.
        
        Args:
            file_path: Path to file
            
        Returns:
            SHA-256 hash as hexadecimal string
        """
        sha256_hash = hashlib.sha256()
        
        with open(file_path, 'rb') as f:
            # Read in chunks for large files
            for chunk in iter(lambda: f.read(4096), b''):
                sha256_hash.update(chunk)
        
        return sha256_hash.hexdigest()
    
    @staticmethod
    def validate_hash(data: bytes, expected_hash: str) -> bool:
        """
        Validates that data hash matches expected hash.
        
        Args:
            data: Binary data to validate
            expected_hash: Expected hash
            
        Returns:
            True if hashes match, False otherwise
        """
        actual_hash = HashValidator.calculate_hash(data)
        return actual_hash.lower() == expected_hash.lower()
    
    @staticmethod
    def validate_hash_from_file(file_path: str, expected_hash: str) -> bool:
        """
        Validates hash of a file.
        
        Args:
            file_path: Path to file
            expected_hash: Expected hash
            
        Returns:
            True if hashes match, False otherwise
        """
        actual_hash = HashValidator.calculate_hash_from_file(file_path)
        return actual_hash.lower() == expected_hash.lower()


class TransmissionPackage:
    """
    Transmission package - contains JSON + Hash.
    This is the payload sent via satellite (few KB instead of MB).
    """
    
    def __init__(self, json_data: Dict[str, Any], document_hash: str):
        """
        Creates a transmission package.
        
        Args:
            json_data: Extracted data in JSON format
            document_hash: SHA-256 hash of generated PDF document
        """
        self.json_data = json_data
        self.document_hash = document_hash
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Converts package to dictionary for serialization.
        
        Returns:
            Dictionary with package structure
        """
        return {
            "version": "1.0.0",
            "data": self.json_data,
            "hash": self.document_hash,
            "metadata": {
                "compression_protocol": "1870_telegraph",
                "hash_algorithm": "SHA-256"
            }
        }
    
    def to_json(self, pretty: bool = False) -> str:
        """
        Serializes package as JSON string.
        
        Args:
            pretty: If True, formats JSON for readability
            
        Returns:
            JSON string
        """
        if pretty:
            return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)
        else:
            return json.dumps(self.to_dict(), ensure_ascii=False)
    
    def save_to_file(self, file_path: str, pretty: bool = True):
        """
        Saves package to a JSON file.
        
        Args:
            file_path: Path where to save
            pretty: If True, formats JSON
        """
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(self.to_json(pretty=pretty))
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TransmissionPackage':
        """
        Creates package from dictionary.
        
        Args:
            data: Dictionary with package structure
            
        Returns:
            TransmissionPackage instance
        """
        return cls(
            json_data=data['data'],
            document_hash=data['hash']
        )
    
    @classmethod
    def from_json(cls, json_string: str) -> 'TransmissionPackage':
        """
        Creates package from JSON string.
        
        Args:
            json_string: JSON string
            
        Returns:
            TransmissionPackage instance
        """
        data = json.loads(json_string)
        return cls.from_dict(data)
    
    @classmethod
    def load_from_file(cls, file_path: str) -> 'TransmissionPackage':
        """
        Loads package from a JSON file.
        
        Args:
            file_path: Path to file
            
        Returns:
            TransmissionPackage instance
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            json_string = f.read()
        return cls.from_json(json_string)
    
    def get_size_kb(self) -> float:
        """
        Returns package size in KB.
        
        Returns:
            Size in kilobytes
        """
        json_str = self.to_json()
        size_bytes = len(json_str.encode('utf-8'))
        return size_bytes / 1024


class IntegrityVerifier:
    """
    Verifies integrity of reconstructed documents.
    Compares hash of reconstructed document with received hash.
    """
    
    @staticmethod
    def verify_reconstruction(
        reconstructed_pdf_bytes: bytes,
        transmission_package: TransmissionPackage
    ) -> Tuple[bool, str]:
        """
        Verifies if reconstructed document is identical to original.
        
        Args:
            reconstructed_pdf_bytes: PDF reconstructed on server
            transmission_package: Package received from client
            
        Returns:
            Tuple (is_valid, message)
        """
        # Calculate hash of reconstructed document
        reconstructed_hash = HashValidator.calculate_hash(reconstructed_pdf_bytes)
        
        # Compare with hash from package
        if reconstructed_hash.lower() == transmission_package.document_hash.lower():
            return True, " Document integrity verified - Perfect match"
        else:
            return False, f" Hash mismatch! Expected: {transmission_package.document_hash}, Got: {reconstructed_hash}"
    
    @staticmethod
    def verify_with_details(
        reconstructed_pdf_bytes: bytes,
        transmission_package: TransmissionPackage
    ) -> Dict[str, Any]:
        """
        Verification with complete details.
        
        Args:
            reconstructed_pdf_bytes: Reconstructed PDF
            transmission_package: Received package
            
        Returns:
            Dictionary with detailed results
        """
        reconstructed_hash = HashValidator.calculate_hash(reconstructed_pdf_bytes)
        expected_hash = transmission_package.document_hash
        is_valid = reconstructed_hash.lower() == expected_hash.lower()
        
        return {
            "valid": is_valid,
            "expected_hash": expected_hash,
            "actual_hash": reconstructed_hash,
            "match": is_valid,
            "pdf_size_bytes": len(reconstructed_pdf_bytes),
            "json_size_kb": transmission_package.get_size_kb(),
            "compression_ratio": len(reconstructed_pdf_bytes) / (transmission_package.get_size_kb() * 1024),
            "message": " Perfect integrity" if is_valid else " Integrity check failed"
        }


# Helper functions for quick use
def create_transmission_package(
    json_data: Dict[str, Any],
    pdf_bytes: bytes
) -> TransmissionPackage:
    """
    Creates transmission package from JSON and PDF.
    
    Args:
        json_data: Extracted data
        pdf_bytes: Generated PDF
        
    Returns:
        Transmission package ready to send
    """
    document_hash = HashValidator.calculate_hash(pdf_bytes)
    return TransmissionPackage(json_data, document_hash)


def verify_received_package(
    transmission_package: TransmissionPackage,
    reconstructed_pdf_bytes: bytes
) -> bool:
    """
    Verifies integrity of received package.
    
    Args:
        transmission_package: Received package
        reconstructed_pdf_bytes: Locally reconstructed PDF
        
    Returns:
        True if document is valid, False otherwise
    """
    is_valid, message = IntegrityVerifier.verify_reconstruction(
        reconstructed_pdf_bytes,
        transmission_package
    )
    print(message)
    return is_valid


if __name__ == "__main__":
    print("Hash Validator & Transmission Package - Ready")
    print("Usage:")
    print("  from shared.hash_validator import create_transmission_package, verify_received_package")
    print("  package = create_transmission_package(json_data, pdf_bytes)")
    print("  is_valid = verify_received_package(package, reconstructed_pdf)")
