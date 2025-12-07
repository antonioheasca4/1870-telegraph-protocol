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
    
    # Transaction Types - MARITIME BANKING FOCUS
    TRANSACTION_TYPES = {
        "swift": {
            "keywords": ["SWIFT", "SWIFT transfer", "SWIFT MT103", "international transfer", "cross-border payment"],
            "aliases": ["Society for Worldwide Interbank Financial Telecommunication", "MT103", "SWIFT payment"],
            "description": "International wire transfer via SWIFT network - PRIMARY for maritime cross-border payments",
            "priority": 1,
            "maritime_context": ["ship-to-shore payments", "international port fees", "foreign supplier payments", "crew salary international"]
        },
        "wire": {
            "keywords": ["wire", "wire transfer", "telegraphic transfer", "urgent transfer", "emergency payment"],
            "aliases": ["TT", "T/T", "cable transfer", "express transfer"],
            "description": "Electronic funds transfer via wire networks - CRITICAL for urgent maritime payments",
            "priority": 1,
            "maritime_context": ["emergency equipment purchase", "urgent port fees", "bunker fuel urgent payment", "detention avoidance"]
        },
        "payment": {
            "keywords": ["payment", "pay", "settlement", "invoice payment", "bill payment", "fee payment"],
            "aliases": ["vendor payment", "supplier payment", "service payment", "disbursement"],
            "description": "Payment for goods or services - MOST COMMON maritime transaction type",
            "priority": 1,
            "maritime_context": ["port charges", "cargo handling fees", "bunker fuel", "provisioning", "container terminal fees", "berthing fees", "pilotage", "towage"]
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
    
    # Maritime-Specific Terms for Banking Transactions
    MARITIME_TERMS = {
        "vessel": {
            "keywords": ["vessel", "ship", "MV", "cargo ship", "container ship", "tanker", "bulk carrier", "VLCC", "oil tanker"],
            "banking_relevance": "Vessel identification in payment descriptions"
        },
        "cargo": {
            "keywords": ["cargo", "freight", "shipment", "container", "TEU", "FEU", "20ft container", "40ft container", "bulk cargo", "general cargo"],
            "banking_relevance": "Cargo details in invoices and L/C documents"
        },
        "port": {
            "keywords": ["port", "harbor", "harbour", "terminal", "berth", "dock", "quay", "wharf", "anchorage"],
            "banking_relevance": "Payment recipient or service location"
        },
        "port_operations": {
            "keywords": ["berthing", "unberthing", "mooring", "loading", "unloading", "discharge", "stevedoring", "cargo handling", "lashing", "unlashing"],
            "banking_relevance": "Service descriptions in payment purposes"
        },
        "port_fees": {
            "keywords": ["port charges", "port dues", "berthing fees", "pilotage", "towage", "tug assistance", "linesmen", "mooring fees", "wharfage", "quayage"],
            "banking_relevance": "PAYMENT type - specific port authority charges"
        },
        "cargo_fees": {
            "keywords": ["cargo handling", "stevedore fees", "loading charges", "unloading fees", "terminal handling charges", "THC", "container handling"],
            "banking_relevance": "PAYMENT type - cargo operation costs"
        },
        "storage_fees": {
            "keywords": ["demurrage", "detention", "storage charges", "container storage", "yard storage", "free time", "overstay charges"],
            "banking_relevance": "PAYMENT type - penalty fees for delays"
        },
        "bunker": {
            "keywords": ["bunker", "fuel", "marine fuel", "marine diesel", "HFO", "heavy fuel oil", "MGO", "marine gas oil", "fuel oil", "bunkering"],
            "banking_relevance": "PAYMENT type - fuel supply for vessel"
        },
        "provisioning": {
            "keywords": ["provisions", "stores", "victuals", "supplies", "ship supplies", "chandler", "ship chandlery"],
            "banking_relevance": "PAYMENT type - food and supplies for crew"
        },
        "crew": {
            "keywords": ["crew", "crew salary", "wages", "seamen wages", "crew payment", "payroll", "crew change", "repatriation"],
            "banking_relevance": "WIRE/SWIFT type - crew compensation and repatriation"
        },
        "documentation": {
            "keywords": ["Bill of Lading", "B/L", "BOL", "sea waybill", "manifest", "cargo manifest", "bill of entry", "customs clearance"],
            "banking_relevance": "Reference documents in payment descriptions"
        },
        "trade_finance": {
            "keywords": ["Letter of Credit", "L/C", "LC", "documentary credit", "standby L/C", "bank guarantee", "performance bond"],
            "banking_relevance": "SWIFT type - trade finance instruments"
        }
    }
    
    BANKING_TERMS = {
        "institutions": ["bank", "financial institution", "credit institution", "savings bank"],
        "departments": ["treasury", "trade finance", "corporate banking", "commercial banking"],
        "products": ["letter of credit", "L/C", "LC", "guarantee", "standby LC", "documentary credit"],
        "compliance": ["AML", "KYC", "anti-money laundering", "know your customer", "sanctions screening"]
    }
    
    # Validation Rules - Maritime Banking Focus
    VALIDATION_RULES = {
        "required_fields": ["transaction_type", "sender_name", "receiver_name", "amount", "currency"],
        "valid_transaction_types": ["swift", "wire", "payment"],  # MARITIME FOCUS ONLY
        "amount_validation": {
            "min_value": 0.01,
            "max_value": 999999999.99,
            "decimals": 2,
            "typical_maritime_ranges": {
                "port_fees": [1000, 100000],
                "bunker_fuel": [10000, 500000],
                "cargo_handling": [5000, 200000],
                "crew_salary": [2000, 50000],
                "provisioning": [500, 20000]
            }
        },
        "iban_countries": ["RO", "DE", "FR", "IT", "ES", "NL", "BE", "AT", "CH", "GB", "DK", "NO", "SE", "GR", "MT"],  # Added maritime EU countries
        "swift_pattern": r"^[A-Z]{6}[A-Z0-9]{2}([A-Z0-9]{3})?$",
        "maritime_keywords": [
            "vessel", "ship", "port", "cargo", "container", "TEU", "bunker", "fuel",
            "berthing", "pilotage", "towage", "stevedore", "terminal", "freight",
            "Bill of Lading", "B/L", "manifest", "demurrage", "detention"
        ]
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

Transaction Types (MARITIME BANKING FOCUS - recognize any of these):
"""
        # Generate transaction types from TRANSACTION_TYPES dictionary
        for tx_type, details in cls.TRANSACTION_TYPES.items():
            keywords = ", ".join(details["keywords"][:4])
            aliases = ", ".join(details["aliases"][:3]) if details["aliases"] else ""
            maritime_ctx = ", ".join(details.get("maritime_context", [])[:3])
            prompt += f"- {tx_type.upper()} (Priority {details.get('priority', 2)}): {keywords}"
            if aliases:
                prompt += f" (also: {aliases})"
            if maritime_ctx:
                prompt += f"\n  Maritime use: {maritime_ctx}"
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
        prompt += "\nMARITIME INDUSTRY TERMS (Banking Context):\n"
        prompt += "CRITICAL: This system is specialized for MARITIME BANKING transactions.\n"
        prompt += "If the document contains maritime/shipping terminology, it is likely a valid banking document.\n\n"
        
        for category, details in cls.MARITIME_TERMS.items():
            if isinstance(details, dict):
                terms_list = " / ".join(details["keywords"][:5])
                prompt += f"- {category.upper().replace('_', ' ')}: {terms_list}\n"
                prompt += f"  Banking relevance: {details['banking_relevance']}\n"
            else:
                # Fallback for old format
                terms_list = " / ".join(details[:4])
                prompt += f"- {terms_list.title()}: {category} information\n"
        
        # Generate Banking Terms from BANKING_TERMS
        prompt += "\nBanking Industry Terms (if present):\n"
        for category, terms in cls.BANKING_TERMS.items():
            terms_list = " / ".join(terms[:3])
            prompt += f"- {terms_list.title()}: {category}\n"
        
        # Generate VALIDATION REQUIREMENTS from VALIDATION_RULES
        prompt += "\nVALIDATION REQUIREMENTS (MARITIME BANKING):\n"
        prompt += "1. transaction_type: MUST be one of: swift, wire, payment\n"
        prompt += "   - Use 'swift' for international/cross-border payments\n"
        prompt += "   - Use 'wire' for urgent/emergency transfers\n"
        prompt += "   - Use 'payment' for invoices, port fees, services\n"
        prompt += "2. sender_name: required (shipping company, vessel operator, or individual)\n"
        prompt += "3. receiver_name: required (port authority, supplier, service provider)\n"
        prompt += "4. amount: required, positive number\n"
        prompt += "   - Typical maritime ranges: port fees (€1K-100K), bunker (€10K-500K), cargo handling (€5K-200K)\n"
        prompt += "5. currency: required, standard 3-letter code (EUR, USD, GBP most common in maritime)\n"
        
        prompt += "6. sender_account/receiver_account: optional but extract if present\n"
        prompt += "7. date: optional, use ISO format YYYY-MM-DD\n"
        prompt += "8. reference_number: optional, extract any reference/invoice numbers\n"
        prompt += "9. description: optional, summarize payment purpose\n"
        
        prompt += """
MARITIME BANKING EXTRACTION PRIORITIES:
1. Transaction type detection:
   - Look for SWIFT/MT103/international → type: "swift"
   - Look for urgent/emergency/wire → type: "wire"  
   - Look for invoice/payment/fees/charges → type: "payment"
2. Maritime context recognition:
   - Vessel names, IMO numbers → include in description
   - Port names, terminal info → critical for payment context
   - Cargo details (TEU, containers) → include in additional_info
   - Service types (berthing, pilotage, bunker) → indicates payment purpose
3. Field extraction:
   - Exact matches of field labels from codebook
   - Contextual understanding (e.g., "From: Company A" = sender)
   - Pattern matching (IBAN format, currency symbols)
   - Maritime terminology (vessel, port, cargo) → validates document authenticity

SEMANTIC COMPRESSION RULES (CRITICAL FOR BANDWIDTH OPTIMIZATION):
To optimize for satellite/maritime bandwidth, extract data in CONCISE format:

1. **Use CODES instead of full text where possible:**
   - Countries: Use ISO codes (NO for Norway, NL for Netherlands, DE for Germany)
   - Vessel flags: ISO country codes (NO, LR, PA, MT)
   - Currencies: 3-letter codes only (EUR, USD, GBP)
   - Priorities: IMMEDIATE, HIGH, NORMAL, LOW (not full sentences)

2. **Compress verbose descriptions:**
   - BAD: "This is an urgent emergency wire transfer for bunker fuel purchase due to fuel contamination on MV Nordic Explorer"
   - GOOD: "Emergency bunker fuel - contamination MV Nordic Explorer"
   - Extract KEY FACTS only, remove filler words

3. **Numeric precision:**
   - Amounts: Use exact numbers (120000, not "approximately 120,000 euros")
   - Coordinates: Short format (52°N 4°E, not "52 degrees North, 4 degrees East")
   - Remove units where obvious (TEU instead of "TEU containers")

4. **Contact info:**
   - Phone: +47224810 (remove spaces/dashes)
   - Email: As-is (don't describe, just extract)
   - Names: Full names only, no titles (Erik Olsen, not "Captain Erik Olsen, Master")

5. **Remove redundancy:**
   - Don't repeat information already in other fields
   - If sender_name = "Ocean Freight AS", don't put "Ocean Freight AS from Oslo" in description
   - Vessel name goes in vessel_name field, NOT in description

6. **Nested objects - keep MINIMAL:**
   - Only include essential sub-fields
   - execution_details: {priority: "IMMEDIATE", timeframe: "2h"} not full sentences
   - Use abbreviations: "2h" not "within 2 hours", "80NM" not "80 nautical miles"

7. **Dates/Times:**
   - ISO format: 2025-12-07 (not "December 7th, 2025")
   - Time: 03:45 or 0345 (not "3:45 AM UTC")
   - Deadlines: 2025-12-09 (not "by December 9th, 2025")

MULTI-LANGUAGE SUPPORT:
The codebook terms above are provided in English, but you may encounter the same
banking concepts in OTHER LANGUAGES (Romanian, German, French, Spanish, etc.). Recognize and
extract banking information regardless of the language used in the document. For example:
- "Expeditor" / "Sender" / "Absender" / "Expéditeur" all mean SENDER
- "Beneficiar" / "Receiver" / "Empfänger" / "Bénéficiaire" all mean RECEIVER
- "Suma" / "Amount" / "Betrag" / "Montant" all mean AMOUNT
- "Navă" / "Vessel" / "Schiff" / "Navire" all mean VESSEL
- "Port" / "Haven" / "Hafen" all mean PORT

Use the codebook as a semantic guide, not a literal word-matching dictionary.

REMEMBER: This system is SPECIALIZED for maritime banking. If you see shipping/port/vessel
terminology combined with payment information, it is almost certainly a valid banking document.
CRITICAL: Extract data in COMPRESSED format to minimize satellite bandwidth costs.
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
        """Check if transaction type is valid (maritime focus: swift, wire, payment only)."""
        valid_types = ["swift", "wire", "payment"]
        return tx_type.lower() in valid_types
    
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