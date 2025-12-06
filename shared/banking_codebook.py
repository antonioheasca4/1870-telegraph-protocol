"""
Banking Codebook - Glossary of banking terms and patterns for AI extraction

This module provides a structured glossary of banking terminology, transaction types,
field patterns, and extraction rules to improve AI accuracy in banking document processing.
"""

from typing import Dict, List, Any


class BankingCodebook:
    """
    A comprehensive glossary of banking terms and extraction patterns.
    Used to guide AI extraction and ensure consistent field recognition.
    """
    
    # Transaction Types
    TRANSACTION_TYPES = {
        "transfer": {
            "keywords": ["transfer", "wire transfer", "bank transfer", "fund transfer", "remittance"],
            "aliases": ["SWIFT transfer", "SEPA transfer", "ACH transfer", "international transfer"],
            "description": "Movement of funds between accounts"
        },
        "payment": {
            "keywords": ["payment", "pay", "settlement", "disbursement"],
            "aliases": ["invoice payment", "bill payment", "vendor payment"],
            "description": "Payment for goods or services"
        },
        "wire": {
            "keywords": ["wire", "wire transfer", "telegraphic transfer"],
            "aliases": ["TT", "T/T", "cable transfer"],
            "description": "Electronic funds transfer via wire networks"
        },
        "swift": {
            "keywords": ["SWIFT", "SWIFT transfer", "SWIFT MT103"],
            "aliases": ["Society for Worldwide Interbank Financial Telecommunication"],
            "description": "International wire transfer via SWIFT network"
        },
        "sepa": {
            "keywords": ["SEPA", "SEPA transfer", "SEPA credit transfer"],
            "aliases": ["Single Euro Payments Area", "SCT"],
            "description": "Euro payment within SEPA zone"
        },
        "ach": {
            "keywords": ["ACH", "ACH transfer", "automated clearing house"],
            "aliases": ["direct deposit", "direct debit"],
            "description": "Electronic batch payment system (USA)"
        }
    }
    
    # Field Patterns
    FIELD_PATTERNS = {
        "sender": {
            "labels": ["sender", "payer", "debtor", "remitter", "from", "originator", "client"],
            "context": "Entity initiating the transaction",
            "required_subfields": ["name"],
            "optional_subfields": ["account", "address", "reference"]
        },
        "receiver": {
            "labels": ["receiver", "payee", "beneficiary", "creditor", "to", "recipient"],
            "context": "Entity receiving the transaction",
            "required_subfields": ["name"],
            "optional_subfields": ["account", "address", "reference"]
        },
        "amount": {
            "labels": ["amount", "sum", "total", "value", "payment amount", "transfer amount"],
            "context": "Monetary value of transaction",
            "patterns": [
                r"\d+[,.]?\d*\s*(EUR|USD|GBP|CHF|RON)",  # 5000 EUR
                r"(EUR|USD|GBP|CHF|RON)\s*\d+[,.]?\d*",  # EUR 5000
                r"\$\s*\d+[,.]?\d*",  # $ 5000
                r"€\s*\d+[,.]?\d*",   # € 5000
            ],
            "validation": "Must be positive number"
        },
        "currency": {
            "labels": ["currency", "ccy", "denomination"],
            "valid_codes": ["EUR", "USD", "GBP", "CHF", "JPY", "RON", "CNY", "AUD", "CAD", "SEK"],
            "symbols": {
                "€": "EUR",
                "$": "USD",
                "£": "GBP",
                "¥": "JPY",
                "Fr": "CHF"
            }
        },
        "account": {
            "labels": ["account", "account number", "acc no", "a/c", "acct"],
            "formats": {
                "IBAN": r"[A-Z]{2}\d{2}[A-Z0-9]{1,30}",  # RO49AAAA1B31007593840000
                "SWIFT": r"[A-Z]{4}[A-Z]{2}[A-Z0-9]{2}([A-Z0-9]{3})?",  # RZBR-RO-BB
                "Generic": r"\d{8,34}"  # 8-34 digits
            },
            "examples": ["RO49AAAA1B31007593840000", "DE89370400440532013000"]
        },
        "date": {
            "labels": ["date", "transaction date", "value date", "execution date", "payment date"],
            "formats": [
                "%Y-%m-%d",      # 2025-12-06
                "%d/%m/%Y",      # 06/12/2025
                "%d.%m.%Y",      # 06.12.2025
                "%B %d, %Y",     # December 6, 2025
            ]
        },
        "reference": {
            "labels": ["reference", "ref", "transaction ref", "payment ref", "invoice ref", "order ref"],
            "patterns": [
                r"[A-Z]{2,4}-\d{4}-\d{4,8}",  # MSK-2025-1234
                r"INV-\d{4}-\d{2}-\d{3}",     # INV-2025-12-001
                r"REF\d{8,12}"                # REF20251206001
            ]
        },
        "description": {
            "labels": ["description", "purpose", "payment purpose", "details", "narrative", "memo"],
            "context": "Explanation of transaction purpose",
            "common_phrases": [
                "payment for invoice",
                "service fees",
                "cargo handling",
                "container transport",
                "fuel supply",
                "port charges"
            ]
        }
    }
    
    # Industry-Specific Terms
    MARITIME_TERMS = {
        "vessel": ["vessel", "ship", "MV", "cargo ship", "container ship", "tanker"],
        "cargo": ["cargo", "freight", "shipment", "container", "TEU", "FEU"],
        "port": ["port", "harbor", "terminal", "berth", "dock"],
        "route": ["route", "voyage", "journey", "shipping lane"],
        "fees": ["port charges", "berthing fees", "cargo handling", "demurrage", "detention"]
    }
    
    BANKING_TERMS = {
        "institutions": ["bank", "financial institution", "credit institution", "savings bank"],
        "departments": ["treasury", "trade finance", "corporate banking", "commercial banking"],
        "products": ["letter of credit", "L/C", "LC", "guarantee", "standby LC", "documentary credit"],
        "compliance": ["AML", "KYC", "anti-money laundering", "know your customer", "sanctions screening"]
    }
    
    # Validation Rules
    VALIDATION_RULES = {
        "required_fields": ["transaction_type", "sender_name", "receiver_name", "amount", "currency"],
        "amount_validation": {
            "min_value": 0.01,
            "max_value": 999999999.99,
            "decimals": 2
        },
        "iban_countries": ["RO", "DE", "FR", "IT", "ES", "NL", "BE", "AT", "CH", "GB"],
        "swift_pattern": r"^[A-Z]{6}[A-Z0-9]{2}([A-Z0-9]{3})?$"
    }
    
    @classmethod
    def get_extraction_prompt_enhancement(cls) -> str:
        """
        Generate enhanced prompt section with codebook terminology.
        This should be appended to the main AI extraction prompt.
        Uses data from TRANSACTION_TYPES, FIELD_PATTERNS, MARITIME_TERMS, etc.
        """
        prompt = """

BANKING CODEBOOK - TERMINOLOGY REFERENCE:

Transaction Types (recognize any of these):
"""
        # Generate transaction types from TRANSACTION_TYPES dictionary
        for tx_type, details in cls.TRANSACTION_TYPES.items():
            keywords = ", ".join(details["keywords"][:3])
            aliases = ", ".join(details["aliases"][:2]) if details["aliases"] else ""
            prompt += f"- {tx_type.upper()}: {keywords}"
            if aliases:
                prompt += f" (also: {aliases})"
            prompt += f"\n"
        
        prompt += """
Field Recognition Patterns:

"""
        # Generate SENDER field patterns from FIELD_PATTERNS
        sender_labels = " / ".join(cls.FIELD_PATTERNS["sender"]["labels"][:7]).upper()
        prompt += f"{sender_labels} fields indicate:\n"
        prompt += f"- {cls.FIELD_PATTERNS['sender']['context']}\n"
        prompt += "- Extract: name, account number (IBAN/account), address if available\n\n"
        
        # Generate RECEIVER field patterns from FIELD_PATTERNS
        receiver_labels = " / ".join(cls.FIELD_PATTERNS["receiver"]["labels"][:6]).upper()
        prompt += f"{receiver_labels} fields indicate:\n"
        prompt += f"- {cls.FIELD_PATTERNS['receiver']['context']}\n"
        prompt += "- Extract: name, account number (IBAN/account), address if available\n\n"
        
        # Generate AMOUNT field patterns from FIELD_PATTERNS
        amount_labels = " / ".join(cls.FIELD_PATTERNS["amount"]["labels"][:4]).upper()
        prompt += f"{amount_labels} fields indicate:\n"
        prompt += f"- {cls.FIELD_PATTERNS['amount']['context']}\n"
        prompt += '- May appear as: "5,000 EUR", "EUR 5,000", "$5,000", "€5,000"\n\n'
        
        # Generate CURRENCY codes from FIELD_PATTERNS
        currency_codes = ", ".join(cls.FIELD_PATTERNS["currency"]["valid_codes"])
        prompt += "CURRENCY codes:\n"
        prompt += f"- Standard: {currency_codes}\n"
        prompt += "- Symbols: € (EUR), $ (USD), £ (GBP), ¥ (JPY)\n\n"
        
        # Generate ACCOUNT NUMBER formats from FIELD_PATTERNS
        account_labels = " / ".join(cls.FIELD_PATTERNS["account"]["labels"][:5]).upper()
        prompt += f"{account_labels} formats:\n"
        prompt += "- IBAN: 2 letters + 2 digits + up to 30 alphanumeric (e.g., RO49AAAA1B31007593840000)\n"
        prompt += "- Generic: 8-34 digits\n\n"
        
        # Generate DATE formats from FIELD_PATTERNS
        date_labels = " / ".join(cls.FIELD_PATTERNS["date"]["labels"][:5]).upper()
        prompt += f"{date_labels} formats:\n"
        prompt += "- ISO: 2025-12-06\n"
        prompt += "- EU: 06/12/2025 or 06.12.2025\n"
        prompt += "- US: December 6, 2025\n\n"
        
        # Generate REFERENCE patterns from FIELD_PATTERNS
        reference_labels = " / ".join(cls.FIELD_PATTERNS["reference"]["labels"][:6]).upper()
        prompt += f"{reference_labels} patterns:\n"
        prompt += "- Invoice: INV-2025-12-001\n"
        prompt += "- Transaction: MSK-2025-1234\n"
        prompt += "- Generic: REF20251206001\n\n"
        
        # Generate Maritime Industry Terms from MARITIME_TERMS
        prompt += "Maritime Industry Terms (if present):\n"
        for category, terms in cls.MARITIME_TERMS.items():
            terms_list = " / ".join(terms[:4])
            prompt += f"- {terms_list.title()}: {category} information\n"
        
        # Generate Banking Terms from BANKING_TERMS
        prompt += "\nBanking Industry Terms (if present):\n"
        for category, terms in cls.BANKING_TERMS.items():
            terms_list = " / ".join(terms[:3])
            prompt += f"- {terms_list.title()}: {category}\n"
        
        # Generate VALIDATION REQUIREMENTS from VALIDATION_RULES
        prompt += "\nVALIDATION REQUIREMENTS:\n"
        required_fields = cls.VALIDATION_RULES["required_fields"]
        for i, field in enumerate(required_fields, 1):
            if field == "transaction_type":
                tx_types = ", ".join(cls.TRANSACTION_TYPES.keys())
                prompt += f"{i}. {field}: must match one of: {tx_types}\n"
            elif field == "amount":
                prompt += f"{i}. {field}: required, must be positive number\n"
            elif field == "currency":
                prompt += f"{i}. {field}: required, use standard 3-letter code (EUR, USD, etc.)\n"
            else:
                prompt += f"{i}. {field}: required (company or person name)\n"
        
        prompt += "6. sender_account/receiver_account: optional but extract if present\n"
        prompt += "7. date: optional, use ISO format YYYY-MM-DD\n"
        prompt += "8. reference_number: optional, extract any reference/invoice numbers\n"
        prompt += "9. description: optional, summarize payment purpose\n"
        
        prompt += """
When extracting, prioritize:
1. Exact matches of field labels from codebook
2. Contextual understanding (e.g., "From: Company A" = sender)
3. Pattern matching (IBAN format, currency symbols)
4. Industry context (maritime, banking terms)

IMPORTANT: The codebook terms above are provided in English, but you may encounter the same
banking concepts in OTHER LANGUAGES (Romanian, German, French, Spanish, etc.). Recognize and
extract banking information regardless of the language used in the document. For example:
- "Expeditor" / "Sender" / "Absender" / "Expéditeur" all mean SENDER
- "Beneficiar" / "Receiver" / "Empfänger" / "Bénéficiaire" all mean RECEIVER
- "Suma" / "Amount" / "Betrag" / "Montant" all mean AMOUNT
Use the codebook as a semantic guide, not a literal word-matching dictionary.
"""
        return prompt
    
    @classmethod
    def get_field_aliases(cls, field_type: str) -> List[str]:
        """Get all possible labels/aliases for a field type."""
        if field_type in cls.FIELD_PATTERNS:
            return cls.FIELD_PATTERNS[field_type].get("labels", [])
        return []
    
    @classmethod
    def validate_transaction_type(cls, tx_type: str) -> bool:
        """Check if transaction type is valid."""
        return tx_type.lower() in cls.TRANSACTION_TYPES
    
    @classmethod
    def validate_currency(cls, currency: str) -> bool:
        """Check if currency code is valid."""
        valid_codes = cls.FIELD_PATTERNS["currency"]["valid_codes"]
        return currency.upper() in valid_codes
    
    @classmethod
    def get_codebook_summary(cls) -> Dict[str, Any]:
        """Get a summary of the codebook for documentation."""
        return {
            "transaction_types": list(cls.TRANSACTION_TYPES.keys()),
            "supported_currencies": cls.FIELD_PATTERNS["currency"]["valid_codes"],
            "required_fields": cls.VALIDATION_RULES["required_fields"],
            "field_count": len(cls.FIELD_PATTERNS),
            "maritime_term_categories": len(cls.MARITIME_TERMS),
            "banking_term_categories": len(cls.BANKING_TERMS)
        }