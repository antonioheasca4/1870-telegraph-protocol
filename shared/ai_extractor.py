"""
AI Extractor Module
Processes unstructured data (text, images, documents) and extracts key information
using Google Gemini API for banking domain.
"""

import os
import json
import base64
from typing import Dict, Any, Optional, Union
from pathlib import Path
import google.generativeai as genai


class AIExtractor:
    """Extracts structured information from unstructured data using Google Gemini API."""
    
    # JSON schema for banking data extraction
    BANKING_SCHEMA = {
        "type": "object",
        "properties": {
            "transaction_type": {
                "type": "string",
                "description": "Transaction type (transfer, contract, request, confirmation, etc.)"
            },
            "sender_name": {
                "type": "string",
                "description": "Full name of sender/client"
            },
            "sender_account": {
                "type": "string",
                "description": "Sender's account number"
            },
            "receiver_name": {
                "type": "string",
                "description": "Full name of receiver"
            },
            "receiver_account": {
                "type": "string",
                "description": "Receiver's account number"
            },
            "amount": {
                "type": "number",
                "description": "Transaction amount"
            },
            "currency": {
                "type": "string",
                "description": "Currency (USD, EUR, RON, etc.)"
            },
            "date": {
                "type": "string",
                "description": "Transaction date in ISO 8601 format (YYYY-MM-DD)"
            },
            "description": {
                "type": "string",
                "description": "Transaction description or reason"
            },
            "reference_number": {
                "type": "string",
                "description": "Transaction reference number"
            },
            "signature_present": {
                "type": "boolean",
                "description": "Whether signature exists in document"
            },
            "additional_info": {
                "type": "string",
                "description": "Any other relevant notes or special instructions from the document (as plain text, not JSON)"
            }
        },
        "required": ["transaction_type", "sender_name", "date"]
    }
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initializes AI extractor.
        
        Args:
            api_key: Google Gemini API key. If not provided, will search in GEMINI_API_KEY environment variable
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("Gemini API key is required. Set GEMINI_API_KEY environment variable or pass it as parameter.")
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        
        # Use Gemini 2.5 Flash model (latest, fast and free)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Configuration for JSON output
        self.generation_config = {
            'temperature': 0.1,  # More deterministic responses
            'top_p': 0.95,
            'top_k': 40,
            'max_output_tokens': 8192,  # Increased for longer documents
        }
    
    def extract_from_text(self, text: str, schema: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Extracts structured information from unstructured text.
        
        Args:
            text: Text to process
            schema: Custom JSON schema (optional, default: BANKING_SCHEMA)
            
        Returns:
            Dict with extracted data
        """
        schema = schema or self.BANKING_SCHEMA
        
        prompt = f"""You are an AI assistant specialized in extracting information from banking documents.
Analyze the provided text and extract all relevant banking information according to the JSON schema.

CRITICAL RULES:
1. If the text does NOT contain banking/financial information, return a JSON with:
   - transaction_type: "unknown"
   - sender_name: "Not found"
   - date: current date (YYYY-MM-DD)
   - All other fields: null or empty strings
   
2. If the text DOES contain banking information:
   - Extract only information explicitly present in text
   - Do not invent or assume information
   - For missing optional fields, use null
   - Respect data types from schema
   
3. For dates, use ISO 8601 format (YYYY-MM-DD)
4. Return ONLY valid JSON, without additional text, without markdown, without ```json```

JSON Schema:
{json.dumps(schema, indent=2)}

Text to analyze:
{text}

JSON:"""
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=self.generation_config
            )
            
            # Extract JSON from response
            response_text = response.text.strip()
            
            # Clean response of any markdown markers
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.startswith('```'):
                response_text = response_text[3:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            
            response_text = response_text.strip()
            
            # Try to parse JSON
            try:
                extracted_data = json.loads(response_text)
            except json.JSONDecodeError as e:
                # Try to recover from truncated JSON
                # Find the last complete field
                last_complete_brace = response_text.rfind('}')
                if last_complete_brace > 0:
                    truncated_json = response_text[:last_complete_brace + 1]
                    try:
                        extracted_data = json.loads(truncated_json)
                        print(f"Warning: Recovered from truncated JSON response")
                    except:
                        raise Exception(f"Failed to parse JSON from Gemini response: {str(e)}\nResponse: {response_text[:500]}")
                else:
                    raise Exception(f"Failed to parse JSON from Gemini response: {str(e)}\nResponse: {response_text[:500]}")
            
            # Validate that banking information was found
            if not self._is_valid_banking_data(extracted_data):
                raise ValueError("No banking information found in the provided text. Please provide a banking document, transfer order, or financial contract.")
            
            return extracted_data
            
        except ValueError as e:
            # Validation errors should be user-friendly
            raise
        except Exception as e:
            if "Failed to parse JSON" in str(e):
                raise
            raise Exception(f"Error extracting data from text: {str(e)}")
    
    def extract_from_image(self, image_path: str, schema: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Extracts structured information from image (scanned contract, document photo, etc.).
        
        Args:
            image_path: Path to image file
            schema: Custom JSON schema (optional, default: BANKING_SCHEMA)
            
        Returns:
            Dict with extracted data
        """
        schema = schema or self.BANKING_SCHEMA
        
        # Check if file exists
        image_path_obj = Path(image_path)
        if not image_path_obj.exists():
            raise FileNotFoundError(f"Image file not found: {image_path}")
        
        prompt = f"""You are an AI assistant specialized in extracting information from banking documents.
Analyze the provided image (contract, invoice, banking form) and extract all relevant information according to the JSON schema.

CRITICAL RULES:
1. If the image does NOT contain banking/financial information, return a JSON with:
   - transaction_type: "unknown"
   - sender_name: "Not found"
   - date: current date (YYYY-MM-DD)
   - All other fields: null or empty strings
   
2. If the image DOES contain banking information:
   - Extract only information explicitly present in image
   - Carefully read handwritten or printed text
   - Do not invent or assume information
   - For missing optional fields, use null
   - Respect data types from schema
   
3. For dates, use ISO 8601 format (YYYY-MM-DD)
4. For signatures, detect if they exist
5. Return ONLY valid JSON, without additional text, without markdown, without ```json```

JSON Schema:
{json.dumps(schema, indent=2)}

JSON:"""
        
        try:
            # Load image
            from PIL import Image
            img = Image.open(image_path)
            
            # Generate content with image
            response = self.model.generate_content(
                [prompt, img],
                generation_config=self.generation_config
            )
            
            # Extract JSON from response
            response_text = response.text.strip()
            
            # Clean response of any markdown markers
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.startswith('```'):
                response_text = response_text[3:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            
            response_text = response_text.strip()
            
            extracted_data = json.loads(response_text)
            
            # Validate that banking information was found
            if not self._is_valid_banking_data(extracted_data):
                raise ValueError("No banking information found in the provided image. Please provide a banking document, transfer order, or financial contract.")
            
            return extracted_data
            
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse JSON from Gemini response: {str(e)}\nResponse: {response.text[:200]}")
        except Exception as e:
            raise Exception(f"Error extracting data from image: {str(e)}")
    
    def extract_from_pdf(self, pdf_path: str, schema: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Extracts structured information from PDF file.
        Uses Gemini's native PDF processing capability.
        
        Args:
            pdf_path: Path to PDF file
            schema: Custom JSON schema (optional, default: BANKING_SCHEMA)
            
        Returns:
            Dict with extracted data
        """
        schema = schema or self.BANKING_SCHEMA
        
        # Check if file exists
        pdf_path_obj = Path(pdf_path)
        if not pdf_path_obj.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        try:
            # Upload PDF to Gemini
            import google.generativeai as genai
            
            # Upload the file
            pdf_file = genai.upload_file(pdf_path)
            
            prompt = f"""You are an AI assistant specialized in extracting information from banking documents.
Analyze the provided PDF document and extract all relevant banking information according to the JSON schema.

CRITICAL RULES:
1. If the PDF does NOT contain banking/financial information, return a JSON with:
   - transaction_type: "unknown"
   - sender_name: "Not found"
   - date: current date (YYYY-MM-DD)
   - All other fields: null or empty strings
   
2. If the PDF DOES contain banking information:
   - Extract only information explicitly present in document
   - Read all pages carefully
   - Do not invent or assume information
   - For missing optional fields, use null
   - Respect data types from schema
   
3. For dates, use ISO 8601 format (YYYY-MM-DD)
4. For signatures, detect if they exist
5. Return ONLY valid JSON, without additional text, without markdown, without ```json```

JSON Schema:
{json.dumps(schema, indent=2)}

JSON:"""
            
            # Generate content with PDF
            response = self.model.generate_content(
                [pdf_file, prompt],
                generation_config=self.generation_config
            )
            
            # Extract JSON from response
            response_text = response.text.strip()
            
            # Clean response
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.startswith('```'):
                response_text = response_text[3:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            
            response_text = response_text.strip()
            
            extracted_data = json.loads(response_text)
            
            # Validate that banking information was found
            if not self._is_valid_banking_data(extracted_data):
                raise ValueError("No banking information found in the provided PDF. Please provide a banking document, transfer order, or financial contract.")
            
            return extracted_data
            
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse JSON from Gemini response: {str(e)}\nResponse: {response.text[:200]}")
        except Exception as e:
            raise Exception(f"Error extracting data from PDF: {str(e)}")
    
    def extract_from_file(self, file_path: str, schema: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Extracts information from file (text, image, or PDF), automatically detecting type.
        
        Args:
            file_path: Path to file
            schema: Custom JSON schema (optional, default: BANKING_SCHEMA)
            
        Returns:
            Dict with extracted data
        """
        file_path_obj = Path(file_path)
        extension = file_path_obj.suffix.lower()
        
        # Image files
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.tiff'}
        # Text files
        text_extensions = {'.txt', '.md', '.json', '.csv'}
        # PDF files
        pdf_extensions = {'.pdf'}
        
        if extension in image_extensions:
            return self.extract_from_image(file_path, schema)
        elif extension in pdf_extensions:
            return self.extract_from_pdf(file_path, schema)
        elif extension in text_extensions:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            return self.extract_from_text(text, schema)
        else:
            raise ValueError(f"Unsupported file type: {extension}. Supported: images (JPG, PNG, etc.), PDF, and text files.")
    
    def _is_valid_banking_data(self, data: Dict[str, Any]) -> bool:
        """
        Validates that extracted data contains actual banking information.
        
        Args:
            data: Extracted data dictionary
            
        Returns:
            True if valid banking data, False otherwise
        """
        # Check if transaction_type indicates no data found
        if data.get('transaction_type', '').lower() in ['unknown', 'not found', '']:
            return False
        
        # Check if critical fields are missing or contain error messages
        critical_fields = ['sender_name', 'receiver_name', 'amount']
        error_indicators = ['not found', 'unknown', 'no information', 'n/a']
        
        for field in critical_fields:
            value = data.get(field)
            if value is None:
                return False
            if isinstance(value, str) and value.lower() in error_indicators:
                return False
        
        # Check if amount is valid (should be > 0)
        amount = data.get('amount')
        if amount is None or (isinstance(amount, (int, float)) and amount <= 0):
            return False
        
        return True


# Helper function for quick use
def extract_banking_data(input_data: Union[str, Path], api_key: Optional[str] = None) -> Dict[str, Any]:
    """
    Helper function for quick banking data extraction.
    
    Args:
        input_data: Direct text or file path
        api_key: Gemini API key (optional)
        
    Returns:
        Dict with extracted data
    """
    extractor = AIExtractor(api_key)
    
    # Check if it's a file path
    if isinstance(input_data, (str, Path)):
        path_obj = Path(input_data)
        if path_obj.exists() and path_obj.is_file():
            return extractor.extract_from_file(str(input_data))
    
    # Otherwise, treat as text
    return extractor.extract_from_text(str(input_data))


if __name__ == "__main__":
    # Exemplu de utilizare
    print("AI Extractor Module (Google Gemini) - Ready")
    print("Usage:")
    print("  from shared.ai_extractor import AIExtractor, extract_banking_data")
    print("  extractor = AIExtractor()")
    print("  data = extractor.extract_from_text('Contract de transfer...')")
