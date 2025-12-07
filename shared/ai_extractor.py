"""
AI Extractor Module
Processes unstructured data (text, images, documents) and extracts key information
using Google Gemini API for banking domain with Banking Codebook integration.
"""

import os
import json
from typing import Dict, Any, Optional, Union
from pathlib import Path
import google.generativeai as genai
from .banking_codebook import BankingCodebook


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
            schema: Custom JSON schema (optional, NOT used in prompt - only for reference)
            
        Returns:
            Dict with extracted data
        """
        # Get codebook-enhanced prompt section
        codebook_enhancement = BankingCodebook.get_extraction_prompt_enhancement()
        
        prompt = f"""You are an AI assistant specialized in extracting information from banking documents.
Your task is to analyze the provided text and extract ALL relevant banking information you can find.

CRITICAL RULES:
1. **Extract ONLY information explicitly present in the text**
   - Do NOT invent, assume, or fabricate any information
   - If a field is not mentioned, omit it from the JSON or set it to null
   - Do NOT add placeholder values or guesses

2. **If the text does NOT contain banking/financial information:**
   - Return a minimal JSON with only: {{"transaction_type": "unknown", "error": "No banking information found"}}
   
3. **If the text DOES contain banking information:**
   - Extract ALL relevant banking fields you can identify
   - You are NOT limited to predefined fields - extract any banking-relevant information
   - Use the Banking Codebook below as a guide for recognizing banking terminology
   - Return a comprehensive JSON with all extracted data

4. **Data formatting:**
   - Dates: Use ISO 8601 format (YYYY-MM-DD)
   - Numbers: Use numeric types for amounts (not strings)
   - Booleans: Use true/false (not "yes"/"no")
   - Strings: Use for text fields (names, descriptions, references)

5. **Output format:**
   - Return ONLY valid JSON, without additional text
   - Do NOT wrap in markdown (no ```json``` blocks)
   - Ensure proper JSON syntax (quotes, commas, braces)

---

The following BANKING CODEBOOK contains terminology, patterns, and field recognition rules
to help you identify and extract banking information accurately. Use this as a reference
guide for understanding banking terms, transaction types, and field formats:

{codebook_enhancement}

---

EXAMPLE OUTPUT FORMATS (maritime banking - COMPRESSED format):

EXAMPLE 1 - SWIFT International Payment (Port Charges):
{{
  "transaction_type": "swift",
  "sender_name": "Maersk Line",
  "sender_account": "DK5000400440116243",
  "sender_bank": "Danske Bank",
  "sender_swift": "DABADKKK",
  "receiver_name": "Hamburg Port Authority",
  "receiver_account": "DE89370400440532013000",
  "receiver_bank": "Deutsche Bank",
  "receiver_swift": "DEUTDEFF",
  "amount": 45000,
  "currency": "EUR",
  "date": "2025-12-06",
  "description": "Port charges - Hamburg CTerm",
  "vessel_name": "MV Maersk Sealand",
  "vessel_imo": "9876543",
  "vessel_flag": "DK",
  "port_name": "Hamburg CTerm",
  "port_berth": "Burchardkai B7",
  "port_arrival_datetime": "2025-12-01T06:00:00Z",
  "port_departure_datetime": "2025-12-05T18:00:00Z",
  "port_time_duration": "4d12h",
  "cargo_total_handling_teu": 330,
  "cargo_type": "Mixed container"
}}

EXAMPLE 2 - WIRE Emergency Transfer (Bunker Fuel):
{{
  "transaction_type": "wire",
  "priority": "IMMEDIATE",
  "sender_name": "Ocean Freight AS",
  "sender_account": "NO9386011117947",
  "sender_bank": "DNB Bank",
  "sender_swift": "DNBANOKKXXX",
  "receiver_name": "Bunker Fuel Supplies BV",
  "receiver_account": "NL91ABNA0417164300",
  "receiver_bank": "ABN AMRO",
  "receiver_swift": "ABNANL2A",
  "amount": 120000,
  "currency": "EUR",
  "date": "2025-12-07",
  "time_utc": "03:45",
  "description": "Emergency bunker - contamination MV Nordic Explorer",
  "vessel_name": "MV Nordic Explorer",
  "vessel_imo": "9123456",
  "vessel_flag": "NO",
  "vessel_current_position": "52°N 4°E",
  "execution_details": {{
    "priority": "IMMEDIATE",
    "timeframe": "2h"
  }},
  "emergency_situation_details": {{
    "reason": "Fuel contamination - urgent bunker supply",
    "fuel_requirements": {{
      "type": "MGO",
      "quantity_mt": 150,
      "delivery_window": "8h"
    }}
  }}
}}

EXAMPLE 3 - PAYMENT Invoice Settlement (Cargo Handling):
{{
  "transaction_type": "payment",
  "sender_name": "MSC",
  "sender_account": "CH9300762011623852957",
  "sender_bank": "UBS Switzerland",
  "sender_swift": "UBSWCHZH80A",
  "receiver_name": "Port de Barcelona - Terminal Catalunya",
  "receiver_account": "ES9121000418450200051332",
  "receiver_bank": "CaixaBank",
  "receiver_swift": "CAIXESBBXXX",
  "amount": 82500,
  "currency": "EUR",
  "date": "2025-12-06",
  "invoice_number": "BCN-BEST-2025-445",
  "invoice_date": "2025-11-26",
  "due_date": "2025-12-11",
  "description": "Container handling - MSC Flaminia Barcelona BEST",
  "vessel_name": "MSC Flaminia",
  "vessel_imo": "9321456",
  "vessel_flag": "LR",
  "vessel_type": "ULCV",
  "port_name": "Barcelona",
  "port_terminal": "BEST",
  "port_berth": "N Quay B5-6",
  "port_time_duration": "5d7h30m",
  "cargo_operations": {{
    "discharged_teu": 2840,
    "loaded_teu": 3150,
    "total_moves_teu": 5990
  }},
  "vat_included": true,
  "vat_rate": 0.21
}}

COMPRESSION RULES (apply consistently):
1. Duration: "4 days, 12 hours" → "4d12h" | "5 days, 7 hours, 30 minutes" → "5d7h30m"
2. Terminals: "Barcelona Europe South Terminal" → "BEST" | "Container Terminal Services" → "CTerm"
3. Berths: "North Quay, Berth 5-6" → "N Quay B5-6"
4. Company names: "Mediterranean Shipping Company (MSC)" → "MSC"
5. Banks: "UBS Switzerland AG" → "UBS Switzerland" | "CaixaBank, S.A." → "CaixaBank"
6. Countries: Use ISO codes → "Switzerland"="CH", "Spain"="ES", "Liberia"="LR"
7. Phone: Remove spaces → "+34 932 986 000" → "+34932986000"
8. Descriptions: CONCISE, remove vessel name if redundant:
   - BAD: "Container handling & terminal services - MSC Flaminia, Barcelona BEST"
   - GOOD: "Container handling - Barcelona BEST"
9. Nested objects: Keep only ESSENTIAL fields:
   - cargo_operations: Only totals (discharged_teu, loaded_teu, total_moves_teu)
   - Remove: detailed breakdowns, lists of cargo types unless critical
   - invoice_summary: Simplify or remove if amount field already covers it
10. Positions: "52 degrees North, 4 degrees East" → "52°N 4°E"
11. Remove redundancy: Don't repeat vessel/port names already in dedicated fields
12. Compliance objects: Simplify to essential status fields only
- Phone: "+49 40 428470" → "+4940428470" (remove spaces)
- Descriptions: Be CONCISE - "Port charges & container terminal fees for MV Maersk Sealand" → "Port charges - Hamburg CTerm"

REMEMBER: Extract ALL relevant fields, but keep values COMPRESSED and CONCISE for satellite bandwidth optimization.

TEXT TO ANALYZE:
{text}

JSON OUTPUT:"""
        
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
            
            # Try to parse JSON with multiple recovery strategies
            try:
                extracted_data = json.loads(response_text)
            except json.JSONDecodeError as e:
                print(f"⚠ JSON parse error: {str(e)}")
                print(f"⚠ Attempting recovery strategies...")
                
                extracted_data = None
                
                # Strategy 1: Fix unterminated strings by closing quotes
                try:
                    # Count quotes to see if odd number (unclosed string)
                    fixed_text = response_text
                    
                    # Find unterminated string and close it
                    lines = fixed_text.split('\n')
                    for i, line in enumerate(lines):
                        # Check if line has unclosed quote
                        if line.count('"') % 2 == 1 and not line.strip().endswith(','):
                            lines[i] = line + '",'
                    
                    fixed_text = '\n'.join(lines)
                    
                    # Try to find last valid closing brace
                    brace_count = 0
                    last_valid_pos = 0
                    for i, char in enumerate(fixed_text):
                        if char == '{':
                            brace_count += 1
                        elif char == '}':
                            brace_count -= 1
                            if brace_count == 0:
                                last_valid_pos = i + 1
                    
                    if last_valid_pos > 0:
                        fixed_text = fixed_text[:last_valid_pos]
                        extracted_data = json.loads(fixed_text)
                        print(f"✓ Recovered using quote closure strategy")
                except:
                    pass
                
                # Strategy 2: Find last complete object
                if not extracted_data:
                    try:
                        # Find outermost closing brace
                        last_brace = response_text.rfind('}')
                        if last_brace > 0:
                            # Try progressively smaller chunks
                            for end_pos in range(last_brace + 1, max(0, last_brace - 500), -1):
                                try:
                                    truncated = response_text[:end_pos]
                                    extracted_data = json.loads(truncated)
                                    print(f"✓ Recovered by truncating to position {end_pos}")
                                    break
                                except:
                                    continue
                    except:
                        pass
                
                # Strategy 3: Retry request to Gemini
                if not extracted_data:
                    print(f"⚠ Retrying request to Gemini...")
                    try:
                        response = self.model.generate_content(
                            prompt + "\n\nIMPORTANT: Return ONLY valid, complete JSON. Close all strings and objects properly.",
                            generation_config=self.generation_config
                        )
                        response_text = response.text.strip()
                        # Clean markdown
                        if response_text.startswith('```json'):
                            response_text = response_text[7:]
                        if response_text.startswith('```'):
                            response_text = response_text[3:]
                        if response_text.endswith('```'):
                            response_text = response_text[:-3]
                        response_text = response_text.strip()
                        
                        extracted_data = json.loads(response_text)
                        print(f"✓ Retry successful")
                    except Exception as retry_error:
                        print(f"✗ Retry failed: {str(retry_error)}")
                
                # If all strategies failed, raise error
                if not extracted_data:
                    raise Exception(f"Failed to parse JSON from Gemini response after all recovery attempts: {str(e)}\nResponse: {response_text[:500]}")
            
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
            schema: Custom JSON schema (optional, NOT used in prompt - only for reference)
            
        Returns:
            Dict with extracted data
        """
        # Check if file exists
        image_path_obj = Path(image_path)
        if not image_path_obj.exists():
            raise FileNotFoundError(f"Image file not found: {image_path}")
        
        # Get codebook-enhanced prompt section
        codebook_enhancement = BankingCodebook.get_extraction_prompt_enhancement()
        
        prompt = f"""You are an AI assistant specialized in extracting information from banking documents.
Your task is to analyze the provided image (contract, invoice, banking form) and extract ALL relevant banking information you can find.

CRITICAL RULES:
1. **Extract ONLY information explicitly visible in the image**
   - Do NOT invent, assume, or fabricate any information
   - If a field is not visible, omit it from the JSON or set it to null
   - Read handwritten and printed text carefully

2. **If the image does NOT contain banking/financial information:**
   - Return a minimal JSON with only: {{"transaction_type": "unknown", "error": "No banking information found"}}
   
3. **If the image DOES contain banking information:**
   - Extract ALL relevant banking fields you can identify
   - You are NOT limited to predefined fields - extract any banking-relevant information
   - Use the Banking Codebook below as a guide for recognizing banking terminology

4. **Data formatting:**
   - Dates: Use ISO 8601 format (YYYY-MM-DD)
   - Numbers: Use numeric types for amounts (not strings)
   - Detect signatures if present (signature_present: true/false)

5. **Output format:**
   - Return ONLY valid JSON, without additional text
   - Do NOT wrap in markdown (no ```json``` blocks)

---

The following BANKING CODEBOOK contains terminology, patterns, and field recognition rules
to help you identify and extract banking information accurately. Use this as a reference
guide for understanding banking terms, transaction types, and field formats:

{codebook_enhancement}

---

EXAMPLE OUTPUT FORMAT (maritime banking - adapt fields as needed):
{{
  "transaction_type": "payment",
  "sender_name": "Maersk Line Ltd",
  "sender_account": "RO49AAAA1B31007593840000",
  "receiver_name": "Rotterdam Port Authority",
  "receiver_account": "NL91ABNA0417164300",
  "amount": 25000,
  "currency": "EUR",
  "date": "2025-12-06",
  "description": "Port charges and cargo handling fees",
  "vessel_name": "Maersk Sealand",
  "port": "Rotterdam Container Terminal",
  "signature_present": true
}}

REMEMBER: Extract ALL relevant fields including maritime context (vessel names, cargo details, port information).

JSON OUTPUT:"""
        
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
            schema: Custom JSON schema (optional, NOT used in prompt - only for reference)
            
        Returns:
            Dict with extracted data
        """
        # Check if file exists
        pdf_path_obj = Path(pdf_path)
        if not pdf_path_obj.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        try:
            # Upload PDF to Gemini
            import google.generativeai as genai
            
            # Upload the file
            pdf_file = genai.upload_file(pdf_path)
            
            # Get codebook-enhanced prompt section
            codebook_enhancement = BankingCodebook.get_extraction_prompt_enhancement()
            
            prompt = f"""You are an AI assistant specialized in extracting information from banking documents.
Your task is to analyze the provided PDF document and extract ALL relevant banking information you can find.

CRITICAL RULES:
1. **Extract ONLY information explicitly present in the PDF**
   - Do NOT invent, assume, or fabricate any information
   - If a field is not mentioned, omit it from the JSON or set it to null
   - Read all pages carefully

2. **If the PDF does NOT contain banking/financial information:**
   - Return a minimal JSON with only: {{"transaction_type": "unknown", "error": "No banking information found"}}
   
3. **If the PDF DOES contain banking information:**
   - Extract ALL relevant banking fields you can identify across all pages
   - You are NOT limited to predefined fields - extract any banking-relevant information
   - Use the Banking Codebook below as a guide for recognizing banking terminology

4. **Data formatting:**
   - Dates: Use ISO 8601 format (YYYY-MM-DD)
   - Numbers: Use numeric types for amounts (not strings)
   - Detect signatures if present (signature_present: true/false)

5. **Output format:**
   - Return ONLY valid JSON, without additional text
   - Do NOT wrap in markdown (no ```json``` blocks)

---

The following BANKING CODEBOOK contains terminology, patterns, and field recognition rules
to help you identify and extract banking information accurately. Use this as a reference
guide for understanding banking terms, transaction types, and field formats:

{codebook_enhancement}

---

EXAMPLE OUTPUT FORMAT (maritime banking PDF - adapt fields as needed):
{{
  "transaction_type": "wire",
  "sender_name": "Ocean Freight Services AS",
  "sender_account": "NO9386011117947",
  "sender_swift": "DNBANOKKXXX",
  "receiver_name": "Hamburg Port Services GmbH",
  "receiver_account": "DE89370400440532013000",
  "receiver_bank": "Deutsche Bank AG",
  "amount": 150000,
  "currency": "EUR",
  "date": "2025-12-06",
  "description": "Urgent bunker fuel payment",
  "reference_number": "BUNKER-2025-1234",
  "vessel_name": "Nordic Explorer",
  "cargo_details": "Bunker fuel 500 MT",
  "port": "Hamburg",
  "additional_info": "Emergency fuel supply for vessel departure"
}}

REMEMBER: Extract ALL relevant fields across all PDF pages. Include maritime context (vessel, port, cargo).

JSON OUTPUT:"""
            
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
