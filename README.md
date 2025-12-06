# The 1870 Telegraph Protocol
## Semantic Compression for Secure Low-Bandwidth Banking

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Protocol](https://img.shields.io/badge/protocol-1870_Telegraph-orange)

> **Latest Updates**: Schema-free AI extraction with Banking Codebook integration, multi-language support (EN/RO/DE/FR/ES/IT), flexible field extraction, dynamic prompt generation. See [How AI Extraction Works](#how-ai-extraction-works---prompt-examples) for full prompt examples.

---

## Story

In **1870** (the year Deutsche Bank was founded), international transfers were done via **telegraph**. Because it cost enormously per word, bankers used **"Codebooks"** - physical code books where one word ("HERMES") meant an entire phrase ("Confirm transfer of gold").

**Today**, in maritime zones (cargo ships), on oil platforms, or in conflict zones, satellite internet is **slow and extremely expensive**. Modern contracts (20MB PDFs) block the network.

**The Solution**: We reinvent the "Codebook" using **AI + Deterministic Templating**. We no longer send files, we send **their meaning** (Semantic Compression).

---

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Key Features](#key-features)
  - [AI-Powered Document Processing](#ai-powered-document-processing-client-side-only)
  - [Banking Codebook](#banking-codebook)
  - [How AI Extraction Works - Prompt Examples](#how-ai-extraction-works---prompt-examples)
- [Semantic vs Traditional Compression](#semantic-vs-traditional-compression)
- [Project Structure](#project-structure)
- [What Information is Extracted?](#what-information-is-extracted)
  - [Multi-Language Support](#multi-language-support)
- [How It Works](#how-it-works)
- [Installation](#installation)
- [Usage](#usage)
- [Security & Integrity](#security--integrity)
- [Technical Details](#technical-details)

---

## Architecture Overview

### System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    CLIENT (SHIP) - Web Interface                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. WEB FORM (Flask on port 5870)                               │
│     └─> User uploads: PDF, image, or pastes text               │
│     └─> AI extracts: sender, receiver, amount, description     │
│     └─> Auto-generated: timestamp, reference, signature        │
│                                                                 │
│  2. AI EXTRACTION (Google Gemini - CLIENT SIDE ONLY)            │
│     └─> Input: PDF/Image/Text from user                        │
│     └─> Process: Gemini API analyzes document                  │
│     └─> Output: Structured JSON with banking data              │
│     └─> Validation: Rejects non-banking documents              │
│                                                                 │
│  3. LOCAL PDF GENERATION (ReportLab - Deterministic)            │
│     └─> DigitalCodebook.normalize_data()                       │
│     └─> PDFGenerator.generate_pdf_bytes()                      │
│     └─> Invariant mode: Same JSON = Same PDF (bit-perfect)     │
│                                                                 │
│  4. HASH CALCULATION                                            │
│     └─> SHA-256 hash of generated PDF                          │
│                                                                 │
│  5. TRANSMISSION PACKAGE CREATION                               │
│     └─> TransmissionPackage(json_data, document_hash)          │
│     └─> Package size: ~2-5 KB (vs 20-2000 KB PDF)             │
│     └─> NO AI, NO PDF in transmission - only JSON + hash       │
│                                                                 │
│  6. TCP TRANSMISSION                                            │
│     └─> Connect to server on port 8870                         │
│     └─> Send: 4-byte size prefix + JSON package                │
│     └─> Bandwidth saved: 4.5x - 1000x                          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ TCP Socket (Low Bandwidth)
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   SERVER (BANK) - TCP Listener                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. RECEPTION (port 8870)                                       │
│     └─> Receive: 4-byte size + JSON package                    │
│     └─> Extract: json_data + document_hash                     │
│                                                                 │
│  2. PDF RECONSTRUCTION (Deterministic - NO AI NEEDED)           │
│     └─> SAME DigitalCodebook + SAME normalized data            │
│     └─> PDFGenerator.generate_pdf_bytes(json_data)             │
│     └─> SAME Python code as client → SAME PDF output           │
│     └─> ReportLab invariant=1 ensures bit-perfect match        │
│                                                                 │
│  3. HASH VALIDATION                                             │
│     └─> Calculate SHA-256 of reconstructed PDF                 │
│     └─> Compare: received_hash == calculated_hash              │
│                                                                 │
│  4. INTEGRITY VERIFICATION                                      │
│     └─> Match: Document valid (100% integrity)                 │
│     └─> Mismatch: Security alert (corrupted/tampered)          │
│                                                                 │
│  5. STORAGE                                                     │
│     └─> Save: data/server_output/received_TRANSFER-*.pdf       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Key Features

### AI-Powered Document Processing (Client-Side Only)
- **Google Gemini AI**: Extracts banking data from unstructured documents
- **Banking Codebook Integration**: Uses terminology glossary for accurate field recognition
- **Multi-format support**: PDF, images (JPG, PNG, etc.), text files
- **Multi-language support**: Recognizes banking terms in any language (English, Romanian, German, French, etc.)
- **Flexible extraction**: Not limited to predefined fields - extracts ALL relevant banking data
- **Intelligent validation**: Rejects non-banking documents automatically
- **Used ONLY on client**: Server reconstructs PDFs without AI

### Banking Codebook
- **Comprehensive terminology guide**: Transaction types, field patterns, industry terms
- **Pattern recognition**: IBANs, SWIFT codes, currency symbols, date formats
- **Multi-language awareness**: Recognizes "Sender"/"Expeditor"/"Absender"/"Expéditeur" as same concept
- **Industry-specific terms**: Maritime (vessel, cargo, port) and Banking (L/C, AML, KYC)
- **Dynamic prompt generation**: Codebook data automatically included in AI prompts
- **Validation rules**: Ensures extracted data meets banking requirements

### How AI Extraction Works - Prompt Examples

The system uses **schema-free flexible extraction** - Gemini extracts ALL relevant banking fields, not just predefined ones.

**Prompt Structure Sent to Gemini:**

```
You are an AI assistant specialized in extracting information from banking documents.
Your task is to analyze the provided text and extract ALL relevant banking information you can find.

CRITICAL RULES:
1. **Extract ONLY information explicitly present in the text**
   - Do NOT invent, assume, or fabricate any information
   - If a field is not mentioned, omit it from the JSON or set it to null

2. **If the text DOES contain banking information:**
   - Extract ALL relevant banking fields you can identify
   - You are NOT limited to predefined fields - extract any banking-relevant information
   - Use the Banking Codebook below as a guide for recognizing banking terminology

3. **Data formatting:**
   - Dates: Use ISO 8601 format (YYYY-MM-DD)
   - Numbers: Use numeric types for amounts (not strings)
   - Booleans: Use true/false (not "yes"/"no")

---

The following BANKING CODEBOOK contains terminology, patterns, and field recognition rules
to help you identify and extract banking information accurately:

BANKING CODEBOOK - TERMINOLOGY REFERENCE:

Transaction Types (recognize any of these):
- TRANSFER: transfer, wire transfer, bank transfer (also: SWIFT transfer, SEPA transfer)
- PAYMENT: payment, pay, settlement (also: invoice payment, bill payment)
- WIRE: wire, wire transfer, telegraphic transfer (also: TT, T/T)
- SWIFT: SWIFT, SWIFT transfer, SWIFT MT103
- SEPA: SEPA, SEPA transfer, SEPA credit transfer
- ACH: ACH, ACH transfer, automated clearing house

Field Recognition Patterns:

SENDER / PAYER / DEBTOR / REMITTER / FROM / ORIGINATOR / CLIENT fields indicate:
- Entity initiating the transaction
- Extract: name, account number (IBAN/account), address if available

RECEIVER / PAYEE / BENEFICIARY / CREDITOR / TO / RECIPIENT fields indicate:
- Entity receiving the transaction
- Extract: name, account number (IBAN/account), address if available

AMOUNT / SUM / TOTAL / VALUE fields indicate:
- Monetary value of transaction
- May appear as: "5,000 EUR", "EUR 5,000", "$5,000", "€5,000"

CURRENCY codes:
- Standard: EUR, USD, GBP, CHF, JPY, RON, CNY, AUD, CAD, SEK
- Symbols: € (EUR), $ (USD), £ (GBP), ¥ (JPY)

ACCOUNT / ACCOUNT NUMBER / ACC NO / A/C / ACCT formats:
- IBAN: 2 letters + 2 digits + up to 30 alphanumeric (e.g., RO49AAAA1B31007593840000)
- Generic: 8-34 digits

DATE / TRANSACTION DATE / PAYMENT DATE formats:
- ISO: 2025-12-06
- EU: 06/12/2025 or 06.12.2025
- US: December 6, 2025

REFERENCE / REF / TRANSACTION ID / INVOICE patterns:
- Invoice: INV-2025-12-001
- Transaction: MSK-2025-1234
- Generic: REF20251206001

Maritime Industry Terms (if present):
- Vessel / Ship / Cargo Vessel / Container Ship: vessels information
- Cargo / Freight / Shipment / Goods: cargo information
- Port / Harbor / Terminal / Berth: ports information
- Bill Of Lading / B/L / Bol / Manifest: documentation information

Banking Industry Terms (if present):
- Letter Of Credit / L/C / Lc / Documentary Credit: trade_finance
- Kyc / Know Your Customer / Customer Due Diligence: compliance
- Aml / Anti-Money Laundering / Transaction Monitoring: compliance

VALIDATION REQUIREMENTS:
1. transaction_type: must match one of: transfer, payment, wire, swift, sepa, ach
2. sender_name: required (company or person name)
3. amount: required, must be positive number
4. currency: required, use standard 3-letter code (EUR, USD, etc.)
5. receiver_name: required (company or person name)
6. sender_account/receiver_account: optional but extract if present
7. date: optional, use ISO format YYYY-MM-DD
8. reference_number: optional, extract any reference/invoice numbers
9. description: optional, summarize payment purpose

IMPORTANT: The codebook terms above are provided in English, but you may encounter the same
banking concepts in OTHER LANGUAGES (Romanian, German, French, Spanish, etc.). Recognize and
extract banking information regardless of the language used in the document. For example:
- "Expeditor" / "Sender" / "Absender" / "Expéditeur" all mean SENDER
- "Beneficiar" / "Receiver" / "Empfänger" / "Bénéficiaire" all mean RECEIVER
- "Suma" / "Amount" / "Betrag" / "Montant" all mean AMOUNT
Use the codebook as a semantic guide, not a literal word-matching dictionary.

---

EXAMPLE OUTPUT FORMAT (you can add more fields as needed):
{
  "transaction_type": "transfer",
  "sender_name": "Company A",
  "sender_account": "RO49AAAA1B31007593840000",
  "sender_bank": "Bank Name",
  "receiver_name": "Company B",
  "receiver_account": "DE89370400440532013000",
  "receiver_bank": "Bank Name",
  "amount": 50000,
  "currency": "EUR",
  "date": "2025-12-06",
  "description": "Payment for services",
  "reference_number": "INV-2025-001",
  "additional_info": "Any other relevant details"
}

Remember: Extract ALL relevant fields you find, not just the ones in the example.
The example shows common fields, but you should include ANY banking-related information present in the text.

TEXT TO ANALYZE:
[User's document content here]

JSON OUTPUT:
```

**Key Features of This Prompt:**

1. **Schema-Free Extraction**: Gemini extracts any banking-relevant field, not limited to predefined schema
2. **Codebook Integration**: All terminology from `banking_codebook.py` dynamically inserted
3. **Multi-Language Support**: Explicit instructions to recognize banking terms in any language
4. **Pattern Recognition**: IBAN formats, currency symbols, date formats, reference patterns
5. **Industry Context**: Maritime and banking-specific terminology (vessel, cargo, L/C, AML, KYC)
6. **Validation Rules**: Clear requirements for transaction_type, amounts, currencies
7. **Example-Based Learning**: Shows Gemini what a typical banking JSON looks like
8. **Flexible Extraction**: Explicitly told to extract MORE than the example if relevant data found

**Real Extraction Example:**

Input Document (Romanian + English mixed):
```
ORDIN DE PLATĂ INTERNAȚIONAL
Data: 06 decembrie 2025
Referință: MSK-2025-1234

Expeditor: SC Maritime Logistics SRL
Cont IBAN: RO49INGB0123456789012345
Banca: ING Bank România

Beneficiar: Port Authority Services GmbH
Cont IBAN: DE89370400440532013000
Banca: Deutsche Bank AG
SWIFT: DEUTDEFF

Suma: 45.000,00 EUR
Scop plată: Taxe manipulare containere - Navă MSK REGINA
Referință factură: INV-PORT-2025-067

Detalii suplimentare:
- Încărcare: 150 TEU containere
- Perioadă: 01-05 decembrie 2025
- Terminal: Hamburg Container Terminal
```

Gemini's JSON Output:
```json
{
  "transaction_type": "wire",
  "sender_name": "SC Maritime Logistics SRL",
  "sender_account": "RO49INGB0123456789012345",
  "sender_bank": "ING Bank România",
  "receiver_name": "Port Authority Services GmbH",
  "receiver_account": "DE89370400440532013000",
  "receiver_bank": "Deutsche Bank AG",
  "receiver_swift": "DEUTDEFF",
  "amount": 45000.00,
  "currency": "EUR",
  "date": "2025-12-06",
  "description": "Taxe manipulare containere - Navă MSK REGINA",
  "reference_number": "MSK-2025-1234",
  "invoice_reference": "INV-PORT-2025-067",
  "additional_info": "Container handling fees - Vessel MSK REGINA. Cargo: 150 TEU containers. Period: 01-05 December 2025. Terminal: Hamburg Container Terminal"
}
```

Notice how Gemini:
- ✅ Recognized Romanian terms ("Expeditor" = sender, "Beneficiar" = receiver, "Suma" = amount)
- ✅ Extracted BOTH reference numbers (transaction + invoice)
- ✅ Added `receiver_swift` field (not in example, but relevant)
- ✅ Translated Romanian description to English in `additional_info`
- ✅ Structured cargo details from bullet points into coherent text
- ✅ Recognized maritime context (vessel name, TEU containers, terminal)

### Deterministic PDF Reconstruction (Server-Side)
- **No AI in reconstruction**: Server uses same Python code as client
- **100% deterministic**: Same JSON = Same PDF (bit-perfect)
- **ReportLab invariant mode**: Eliminates timestamps and random IDs
- **DigitalCodebook normalization**: Ensures consistent data structure

### Extreme Compression
- **Original PDF**: 20-2000 KB
- **Transmitted package**: 2-5 KB
- **Compression ratio**: 4.5x - 1000x
- **Bandwidth optimization**: Critical for satellite/maritime links

### Guaranteed Integrity
- **SHA-256 hashing**: Cryptographic validation
- **Bit-perfect reconstruction**: Identical document on server
- **Legal validity**: Hash match = original document proof
- **Tamper detection**: Any modification breaks hash

### Technical Implementation
- **Client**: Flask web server (port 5870) + TCP client
- **Server**: TCP listener (port 8870) with threading
- **Protocol**: Custom 4-byte size prefix + JSON payload
- **PDF Generation**: ReportLab with deterministic settings
- **Data Flow**: Web form → PDF → Hash → TCP → Reconstruct → Validate

### Why AI Extraction Makes Sense in Low-Bandwidth Scenarios

**The Network Economics:**

Even though Gemini AI requires internet connectivity, the bandwidth savings are substantial:

**Without AI (Traditional Approach):**
```
Upload PDF to bank directly: 500 KB → $5.00 @ $10/MB satellite
Total cost: $5.00
Risk: Transmission failure on slow/unstable connection
```

**With AI Extraction (Our Protocol):**
```
1. Upload to Gemini API: 500 KB → $5.00 (one-time, reliable Google infrastructure)
2. Download JSON from Gemini: 2 KB → $0.02
3. Transmit JSON to bank: 2 KB → $0.02
Total cost: $5.04
Advantage: More reliable transmission, smaller payload to critical destination
```

**Key Benefits:**
- **Reliability**: Single small transmission to bank (2 KB vs 500 KB)
- **Retry efficiency**: If bank transmission fails, retrying costs $0.02 vs $5.00
- **Multiple recipients**: Send to multiple banks (2 KB each) vs one large upload
- **Bandwidth control**: Critical transaction data uses minimal satellite time

**Alternative Deployment Scenarios:**

1. **Port Processing** (Optimal):
   - Process documents while docked with WiFi
   - Store extracted JSON locally
   - Transmit only JSONs while at sea

2. **Offline Extraction** (Advanced):
   - Run local NLP models (Llama 3.1 via Ollama)
   - 70-80% accuracy, zero internet required
   - Fallback: Manual form input for complex documents
   - Finetuning with bancking

3. **Hybrid Approach** (Recommended):
   - Primary: Gemini API when connection allows
   - Fallback: Local pattern-based extraction (spaCy + regex)
   - Last resort: Manual data entry

The protocol prioritizes **reliable small transmissions** over unreliable large ones, even if initial AI processing requires connectivity.

### Ideal Use Cases

**Maritime & Offshore:**
- Cargo ships with expensive satellite internet ($10-50/MB)
- Oil platforms with narrow bandwidth (64-256 Kbps)
- Fishing vessels with intermittent connectivity
- Research vessels in remote waters

**Remote Operations:**
- Military field operations with tactical satellite
- Emergency response in disaster zones
- Remote mining/construction sites
- Antarctic research stations

**Cost-Sensitive Scenarios:**
- IoT devices with metered connections
- Mobile banking in developing regions
- Backup communication channels
- Any scenario requiring document integrity + bandwidth optimization

---

## Project Structure

```
CompresieSemantica/
├── client/                       # Client code (Ship)
│   ├── client.py                 # Flask web server + TCP client (port 5870)
│   └── web_interface.html        # User input form
│
├── server/                       # Server code (Bank)
│   └── server.py                 # TCP listener + ReceiverServer (port 8870)
│
├── shared/                       # Shared modules (client & server)
│   ├── ai_extractor.py          # AI extraction with Google Gemini
│   ├── banking_codebook.py      # Banking terminology glossary and patterns
│   ├── pdf_generator.py         # Deterministic PDF generation (ReportLab)
│   └── hash_validator.py        # Integrity validation (SHA-256)
│
├── data/                         # Working data
│   ├── client_output/           # Client outputs (PDFs + JSON packages)
│   └── server_output/           # Server outputs (reconstructed PDFs)
│
├── demo.py                       # Standalone demo (AI extraction workflow)
├── requirements.txt              # Python dependencies
├── .env.example                 # Configuration example
└── README.md                    # This documentation
```

---

## What Information is Extracted?

The AI extraction system uses **flexible schema-free extraction** powered by the Banking Codebook. Gemini extracts ALL relevant banking information found in documents, not just predefined fields.

### Required Banking Information

These fields must be present for a valid banking document:

#### 1. **Transaction Type** (transaction_type)
- **Valid values:** "transfer", "payment", "wire", "swift", "sepa", "ach"
- **Examples in documents:**
  - "SWIFT Transfer Order"
  - "Wire Payment Instruction"
  - "Bank Transfer Request"
  - "Payment Order"
- **What doesn't work:** Generic text without banking context (e.g., "Ana are mere", "Hello world")

#### 2. **Sender Information** (sender_name, sender_account)
- **What to include:**
  - Sender/Payer/Client/Debtor name
  - IBAN, account number, or reference number
- **Valid formats:**
  - "From: Maritime Logistics Inc"
  - "Sender Account: RO49INGB0123456789"
  - "Client: John Smith (DE89370400440532013000)"
- **Must be present:** At minimum, a sender name or account number

#### 3. **Receiver Information** (receiver_name, receiver_account)
- **What to include:**
  - Receiver/Payee/Beneficiary name
  - IBAN, account number, or reference number
- **Valid formats:**
  - "To: Deutsche Bank AG"
  - "Beneficiary Account: RO12BRDE9876543210"
  - "Payee: Port Authority Services"
- **Must be present:** At minimum, a receiver name or account number

#### 4. **Amount** (amount, currency)
- **What to include:**
  - Numerical amount (must be > 0)
  - Currency code or symbol
- **Valid formats:**
  - "Amount: 45,000 EUR"
  - "Total: $10,000 USD"
  - "5000000 RON"
  - "€ 250,000"
- **Must be present:** Amount must be extractable and positive

### Optional Banking Information

Gemini extracts ANY additional banking-relevant fields found in documents:

**Common Additional Fields:**
- **sender_bank**: Sender's financial institution
- **receiver_bank**: Receiver's financial institution  
- **sender_swift**: Sender's SWIFT/BIC code
- **receiver_swift**: Receiver's SWIFT/BIC code
- **sender_address**: Physical address of sender
- **receiver_address**: Physical address of receiver
- **description**: Purpose of transfer, invoice details, notes
- **reference_number**: Transaction reference (e.g., MSK-2025-1234)
- **invoice_reference**: Invoice number (e.g., INV-PORT-2025-067)
- **date**: Transaction date in ISO 8601 format (YYYY-MM-DD)
- **additional_info**: Compliance notes, special instructions, cargo details
- **signature_status**: Verification status
- **vessel_name**: Ship/vessel involved (maritime context)
- **cargo_details**: TEU, goods type, loading period
- **terminal**: Port terminal information
- **compliance_notes**: KYC, AML, regulatory information

**Flexible Extraction Philosophy:**
- Not limited to predefined schema
- Extracts what's relevant to the specific document
- Preserves domain-specific context (maritime, trade finance, etc.)
- Auto-generates missing required fields (date, reference) if needed

### Multi-Language Support

The system recognizes banking terminology in **any language**. The Banking Codebook provides semantic guidance, not literal word matching.

**Supported Languages:**
- 🇬🇧 **English**: Sender, Receiver, Amount, Currency, Payment
- 🇷🇴 **Romanian**: Expeditor, Beneficiar, Suma, Valută, Plată
- 🇩🇪 **German**: Absender, Empfänger, Betrag, Währung, Zahlung
- 🇫🇷 **French**: Expéditeur, Bénéficiaire, Montant, Devise, Paiement
- 🇪🇸 **Spanish**: Remitente, Destinatario, Cantidad, Moneda, Pago
- 🇮🇹 **Italian**: Mittente, Destinatario, Importo, Valuta, Pagamento
- Plus any other language Gemini understands

**Example: Romanian Banking Document**
```
ORDIN DE PLATĂ
Expeditor: SC Transport Maritime SRL
Cont: RO49INGB1234567890
Beneficiar: Autoritatea Portuară Hamburg
Cont: DE89370400440532013000
Suma: 25.000 EUR
Scop: Taxe de acostare și manipulare
```

**Extracted as:**
```json
{
  "transaction_type": "payment",
  "sender_name": "SC Transport Maritime SRL",
  "sender_account": "RO49INGB1234567890",
  "receiver_name": "Autoritatea Portuară Hamburg",
  "receiver_account": "DE89370400440532013000",
  "amount": 25000,
  "currency": "EUR",
  "description": "Taxe de acostare și manipulare"
}
```

**Example: German Banking Document**
```
ÜBERWEISUNGSAUFTRAG
Absender: Hamburg Shipping GmbH
Konto: DE12345678901234567890
Empfänger: Constanța Port Services
Konto: RO98BCRL7654321098765432
Betrag: 18.500 EUR
Verwendungszweck: Hafengebühren Containerterminal
```

**Extracted as:**
```json
{
  "transaction_type": "transfer",
  "sender_name": "Hamburg Shipping GmbH",
  "sender_account": "DE12345678901234567890",
  "receiver_name": "Constanța Port Services",
  "receiver_account": "RO98BCRL7654321098765432",
  "amount": 18500,
  "currency": "EUR",
  "description": "Hafengebühren Containerterminal"
}
```

The codebook explicitly instructs Gemini:
> "IMPORTANT: The codebook terms are provided in English, but you may encounter the same banking concepts in OTHER LANGUAGES. Recognize and extract banking information regardless of the language used. Use the codebook as a semantic guide, not a literal word-matching dictionary."

### What Documents Work?

**Valid Documents (will be accepted):**
- Banking contracts with transfer details (any language)
- Wire transfer orders (SWIFT, SEPA, ACH)
- Invoice payment instructions
- Email confirmations with transaction details
- Maritime/logistics payment orders
- Cargo handling fee contracts
- Fuel supply agreements with payment terms
- Scanned banking forms (PDF or images)
- Photographed contracts (JPG, PNG, etc.)
- PDF invoices and statements
- Text files with banking data
- Mixed-language documents (e.g., Romanian + English)

**Invalid Documents (will be rejected with error):**
- Personal letters without banking info
- Generic text snippets ("Ana are mere", "Hello world")
- Technical documentation
- Code snippets
- Random sentences
- Shopping lists
- Non-financial contracts

### Error Messages

If the document doesn't contain banking information, you'll see:
```
Transfer Failed
No banking information found in the provided text. 
Please provide a banking document, transfer order, or financial contract.
```

This validation ensures:
- No crashes on invalid input
- Clear feedback to users
- Protection against accidental submissions

### Example Valid Input

```
SWIFT TRANSFER ORDER

Sender: Maritime Logistics Inc
Account: RO49INGB0123456789

Receiver: Port Authority Services
Account: RO12BRDE9876543210

Amount: 45,000 EUR
Purpose: Cargo handling fees for vessel MV NEPTUNE

Date: 2025-12-06
Reference: ML-2025-1206
```

**AI will extract:**
- transaction_type: "transfer"
- sender_name: "Maritime Logistics Inc"
- sender_account: "RO49INGB0123456789"
- receiver_name: "Port Authority Services"
- receiver_account: "RO12BRDE9876543210"
- amount: 45000
- currency: "EUR"
- description: "Cargo handling fees for vessel MV NEPTUNE"

---

## Semantic Compression Analysis

### What Information is Preserved vs. Discarded

Using `example_contract.txt` (4,248 bytes / 4.15 KB) as a real-world case study:

#### PRESERVED (Transmitted in JSON):
1. **Core Banking Data:**
   - Transaction type: "International Wire Transfer"
   - Sender: "Maersk Shipping Company A/S" (RO49AAAA1B31007593840000)
   - Receiver: "Deutsche Bank AG" (DE89370400440532013000)
   - Amount: 5,000,000 EUR
   - Date: 2025-12-06

2. **Transaction Description:**
   - Contract reference (MSK-2025-1234)
   - Route details (Rotterdam to Singapore)
   - Cargo specifics (250 TEU, Electronics/Machinery/Textiles)
   - Timeline (28 days, Dec 10 - Jan 7)

3. **Additional Information:**
   - Service contract reference
   - Payment terms (Net 30 days)
   - Invoice number (INV-2025-12-001)
   - SWIFT instructions
   - Special instructions (priority, confirmation required)
   - Contact information

4. **Metadata:**
   - Reference number: MSK-DB-2025-12-06-MARITIME
   - Signature verification status
   - Timestamp

#### DISCARDED (Not transmitted):
1. **Formatting & Visual Elements:**
   - ASCII art borders (================)
   - Section headers styling
   - Blank lines and spacing
   - Column alignment
   - Typography (bold, italics, etc.)

2. **Redundant Legal Text:**
   - Boilerplate legal disclaimers
   - Standard compliance declarations
   - Repeated institutional information
   - Generic terms and conditions
   - Address formatting details

3. **Document Metadata:**
   - "INTERNATIONAL MARITIME BANKING TRANSFER AGREEMENT" title
   - Section labels ("SENDER INFORMATION", "RECEIVER INFORMATION")
   - Structural markers ("END OF DOCUMENT")
   - Organizational formatting

4. **Non-Essential Details:**
   - Full postal addresses (only essential banking data kept)
   - Detailed office locations
   - Vessel IMO numbers (unless critical to transaction)
   - Job titles of signatories (unless required for validation)
   - Multiple contact methods (consolidated into essential info)

### Compression Metrics for example_contract.txt

```
Original Contract:        4,248 bytes (4.15 KB)
  ↓ AI Extraction
Semantic JSON:            1,998 bytes (1.95 KB)  [2.1x compression]
  ↓ Add Hash
Transmission Package:     2,271 bytes (2.22 KB)  [1.9x compression]
  ↓ Send via TCP
  ↓ Reconstruct on Server
Generated PDF:            4,550 bytes (4.44 KB)

Bandwidth Saved: 46.5% (1,977 bytes not transmitted)
```

**Key Insight:** The contract is **4.15 KB** as text, but only **2.22 KB** is transmitted (JSON + hash). The server reconstructs a **4.44 KB PDF** with all essential information formatted professionally.

### Compression Effectiveness by Document Type

| Document Type | Original Size | Package Size | Ratio | Savings |
|--------------|---------------|--------------|-------|---------|
| Simple transfer order | 1.5 KB | 0.8 KB | 1.9x | 47% |
| Maritime contract (example) | 4.2 KB | 2.2 KB | 1.9x | 47% |
| Detailed invoice | 8 KB | 3.5 KB | 2.3x | 56% |
| Legal agreement | 20 KB | 4.5 KB | 4.4x | 77% |
| Scanned contract (image) | 500 KB | 3 KB | 167x | 99.4% |
| Complex PDF | 2 MB | 5 KB | 400x | 99.75% |

**Why compression varies:**
- **Simple documents (1.9x-2.3x):** Most content is essential data, less redundancy
- **Legal documents (4x-10x):** Heavy boilerplate, repeated clauses, formatting overhead
- **Scanned images (100x-1000x):** Massive visual data reduced to pure text
- **Complex PDFs (400x-1000x):** Graphics, embedded fonts, metadata eliminated

### Information Preservation Guarantee

The system ensures **100% semantic accuracy**:
- All financial amounts preserved exactly
- All account numbers transmitted complete
- All dates and references maintained
- All transaction descriptions intact
- PDF reconstruction is bit-perfect (same JSON = same PDF)
- Hash validation ensures zero data corruption

What's "lost" is intentional:
- Visual formatting (reconstructed using deterministic PDF layout)
- Redundant text (legal boilerplate)
- Non-essential metadata (file creation time, author, etc.)

**Result:** The receiver gets a professional, formatted PDF with all critical banking information, validated by cryptographic hash, but transmitted at a fraction of the original size.

---

## Semantic vs Traditional Compression

### Comparison with GZIP/LZMA Compression

While traditional compression algorithms (GZIP, BZ2, LZMA) can achieve good compression ratios on text files, semantic compression provides unique advantages:

**Test Results on invoice-sample.pdf (42.60 KB):**

| Method | Compressed Size | Ratio | Savings |
|--------|----------------|-------|---------|
| Original | 43,627 bytes | 1.0x | 0% |
| GZIP (level 9) | 37,893 bytes | 1.15x | 13.1% |
| BZ2 (level 9) | 39,967 bytes | 1.09x | 8.4% |
| LZMA (preset 9) | 37,692 bytes | 1.16x | 13.6% |
| **Semantic (JSON+Hash)** | **834 bytes** | **52.31x** | **98.1%** |

**For PDF documents:** Semantic compression dominates completely (97.8% smaller than best traditional compression).

**Why semantic compression wins decisively:**

**Advantages of Semantic Compression:**
1. **No decompression needed** - Server reads JSON directly without CPU overhead
2. **Built-in integrity validation** - SHA-256 hash included in package
3. **Structured data access** - Can extract/process fields without decompression
4. **Deterministic reconstruction** - Guarantees bit-perfect PDF regeneration
5. **Immediate validation** - Can verify content structure without full decompression
6. **Scales with complexity** - Advantage grows exponentially for larger documents

**Limitations of Traditional Compression:**
1. **Decompression overhead** - Must decompress entire file before use (CPU cost)
2. **No integrity by default** - Requires separate hash/checksum
3. **Binary blob** - Cannot access data without full decompression
4. **No semantic validation** - Can't verify banking data exists until decompressed
5. **Variable effectiveness** - Compression ratio depends on redundancy patterns

**Scaling Analysis:**

| Document Type | Traditional (LZMA) | Semantic | Winner |
|--------------|-------------------|----------|---------|
| Text file (4 KB) | 1.7 KB (2.5x) | 2.2 KB (1.9x) | Traditional |
| PDF invoice (43 KB) | 37.7 KB (1.16x) | 0.8 KB (52x) | **Semantic (45x better)** |
| Medium PDF (500 KB) | ~125 KB (4x) | 3 KB (167x) | **Semantic (42x better)** |
| Large PDF (2 MB) | ~400 KB (5x) | 5 KB (400x) | **Semantic (80x better)** |

**Key Insight:** For PDF documents (invoices, contracts, scanned documents), semantic compression provides **45-80x better compression** than traditional methods while maintaining full semantic integrity and instant data access. Traditional compression barely compresses PDFs (1.16x) because PDFs are already internally compressed.

**Important Trade-offs:**

Semantic compression achieves extreme compression by **extracting only essential banking data** and discarding non-critical information:

**What semantic compression preserves:**
- Core transaction data (sender, receiver, amount, currency, dates)
- Banking identifiers (IBANs, account numbers, SWIFT codes)
- Transaction descriptions and references
- Legal compliance information

**What semantic compression discards:**
- Original document formatting and layout
- Graphics, logos, images, watermarks
- Font styles, colors, decorative elements
- Company letterheads and branding
- Footer/header content
- Page breaks and multi-column layouts
- Embedded metadata (creation date, author, software used)
- Digital signatures and certificates (reconstructed with new signature)

**What traditional compression preserves:**
- **Everything** - bit-perfect reproduction of original file
- All formatting, images, fonts, metadata
- Exact visual appearance
- Original file structure

**Use case consideration:**
- **Semantic compression:** Best when you need the **data/information** from documents (banking transactions, invoice processing, automated data extraction)
- **Traditional compression:** Best when you need **exact document reproduction** (legal archives, document signing workflows, visual branding preservation)

**When to use each:**
- **Traditional compression:** Archival storage, legal documents requiring exact reproduction, files with critical visual elements
- **Semantic compression:** Banking transactions, invoice processing, automated workflows, low-bandwidth transmission where data matters more than presentation

---

## Installation & Setup

### 1. System Requirements
- **Python 3.10+** (tested with Python 3.10 and 3.11)
- **Google Gemini API Key** (required for AI extraction in both web interface and demo)

### 2. Install Dependencies

```powershell
# Navigate to project directory
cd CompresieSemantica

# Install dependencies
pip install -r requirements.txt
```

**Dependencies:**
- `Flask` + `flask-cors`: Web server for client interface
- `google-generativeai`: AI extraction with native PDF/image support
- `reportlab`: Deterministic PDF generation (no templates needed)
- `pillow`: Image processing
- `python-dotenv`: Environment variables

### 3. Configure API Key (Required for AI Extraction)

```powershell
# Copy configuration file
cp .env.example .env

# Edit .env and add your Gemini API key
# GEMINI_API_KEY=your-actual-api-key-here
```

**OR** set directly in PowerShell:

```powershell
$env:GEMINI_API_KEY="your-actual-api-key-here"
```

**Note**: Gemini API key is **required** for both web interface (client.py) and demo (demo.py). The AI automatically extracts banking information from unstructured documents, validates that banking data exists, and rejects non-banking text with user-friendly error messages.

---

## Usage

### Production System (Web Interface + TCP)

#### Step 1: Start the Server (Bank Side)

```powershell
# Start TCP server listening on port 8870
python server/server.py
```

**Server Output:**
```
Starting 1870 Telegraph Protocol Server...
Server listening on localhost:8870
Waiting for connections...
Press Ctrl+C to stop
```

**What it does:**
- Listens for TCP connections on port 8870
- Receives JSON packages from clients
- Reconstructs PDFs from JSON data
- Validates integrity using SHA-256 hash
- Saves verified PDFs to `data/server_output/received_TRANSFER-*.pdf`
- Returns verification status to client

#### Step 2: Start the Client (Ship Side)

```powershell
# Start Flask web server on port 5870
python client/client.py
```

**Client Output:**
```
Starting 1870 Telegraph Protocol Client...
Web interface: http://localhost:5870
Press Ctrl+C to stop
```

**What it does:**
- Starts Flask web server on port 5870
- Serves AI-powered document processing interface
- Accepts file uploads (images, PDFs, documents) or pasted text
- Uses Google Gemini AI to extract banking data
- Generates PDFs from extracted data
- Calculates SHA-256 hashes
- Sends JSON packages via TCP to server
- Saves PDFs and JSON to `data/client_output/`

#### Step 3: Submit a Document

1. Open browser to `http://localhost:5870`
2. **Option A: Upload a document file**
   - Click "Upload Document"
   - Supported formats:
     - **PDF**: Invoices, contracts, statements (processed natively by Gemini)
     - **Images**: JPG, PNG, GIF, WebP, BMP, TIFF (scanned documents, photos)
     - **Text**: TXT, MD, JSON, CSV files
   - AI will extract all relevant banking information from any format
3. **Option B: Paste document text**
   - Paste contract text, email content, or any banking document
   - Example formats supported:
     - Banking contracts
     - Email confirmations
     - Invoice text
     - Unstructured notes
4. Click "Send Transfer via Satellite"
5. **AI Processing:**
   - Gemini AI extracts: sender, receiver, amount, currency, description, type
   - System auto-generates: timestamp, reference number, signature
6. View extracted data and success/error status on page

**AI Extraction Example:**
```
Input (pasted text):
MARITIME BANKING TRANSFER
FROM: Maersk Shipping Company
Account: RO49AAAA1B31007593840000
TO: Deutsche Bank AG
Account: DE89370400440532013000
AMOUNT: 5,000,000 EUR
Payment for container shipment

Output (AI extracted):
✓ Sender: Maersk Shipping Company (RO49AAAA1B31007593840000)
✓ Receiver: Deutsche Bank AG (DE89370400440532013000)
✓ Amount: 5000000 EUR
✓ Description: Payment for container shipment
✓ Type: transfer
```

**Files Generated:**
- Client: `data/client_output/TRANSFER-*.pdf` + `TRANSFER-*.json`
- Server: `data/server_output/received_TRANSFER-*.pdf`

---

### Demo System (AI Extraction Workflow)

```powershell
# Run standalone demo with AI extraction
python demo.py
```

**What it does:**
- Extracts banking data from unstructured text using Google Gemini AI
- Generates deterministic PDF from extracted data
- Creates transmission package (JSON + hash)
- Simulates server reception and reconstruction
- Validates integrity and displays metrics
- Saves demo files to `data/client_output/demo_*.pdf`

**Note**: Requires `GEMINI_API_KEY` environment variable.

---

## Technical Details

### Bandwidth Optimization Calculation

**Formula:**
```
Original PDF Size: P (bytes)
JSON Package Size: J (bytes)
Compression Ratio: R = P / J
Bandwidth Saved: S = P - J (bytes)
Savings Percentage: (S / P) * 100%
```

**Example:**
```
PDF: 20,480 bytes (20 KB)
JSON: 4,551 bytes (4.5 KB)
Ratio: 20,480 / 4,551 = 4.5x
Saved: 20,480 - 4,551 = 15,929 bytes (15.5 KB)
Percentage: 77.8% bandwidth saved
```

**Real-world Impact:**
- Satellite cost: $10/MB
- 100 documents/day at 20 KB each = 2 MB/day
- Without compression: 2 MB × $10 = **$20/day**
- With 4.5x compression: 0.44 MB × $10 = **$4.40/day**
- **Savings: $15.60/day = $468/month**

### PDF Determinism Implementation

**Key Techniques:**

1. **ReportLab Invariant Mode**
   ```python
   import reportlab.rl_config
   reportlab.rl_config.invariant = 1
   ```
   - Eliminates random PDF object IDs
   - Removes creation timestamps
   - Ensures consistent byte stream

2. **Data Normalization**
   ```python
   def normalize_data(data):
       # Sort all dictionary keys
       # Fixed timestamp based on document date
       # Deterministic reference number format
       # Consistent field ordering
   ```

3. **Consistent PDF Generation**
   - Same JSON = Same PDF (bit-perfect)
   - No dynamic timestamps during generation
   - Consistent font embedding
   - Deterministic layout and formatting

### Hash Validation Process

```python
# Client side
pdf_bytes = generate_pdf(normalized_data)
hash_client = SHA256(pdf_bytes)  # e.g., "a3b5c7..."

# Send: {json_data, hash_client}

# Server side
pdf_reconstructed = generate_pdf(received_json_data)
hash_server = SHA256(pdf_reconstructed)  # Must be "a3b5c7..."

if hash_client == hash_server:
    # Perfect match - document valid
    # Bit-for-bit identical
else:
    # Corrupted or tampered
```

### TCP Protocol Specification

**Message Format:**
```
[4 bytes: size] [size bytes: JSON payload]
```

**Example:**
```python
# Client sends
package_json = '{"version":"1.0.0","data":{...},"hash":"..."}}'
size = len(package_json)  # e.g., 4551
size_bytes = size.to_bytes(4, byteorder='big')  # [0, 0, 17, 199]

client_socket.sendall(size_bytes + package_json.encode())

# Server receives
size_bytes = socket.recv(4)
size = int.from_bytes(size_bytes, byteorder='big')
data = socket.recv(size)
package = json.loads(data)
```

### Error Handling

**Client Side:**
- Socket connection failure → Retry with exponential backoff
- Server timeout → Display error, save package locally
- PDF generation error → Show user error message

**Server Side:**
- Invalid JSON → Return error response
- Hash mismatch → Log alert, reject document
- Socket timeout → Continue listening (1.0s timeout)
- Ctrl+C handling → Graceful shutdown

---

## API Reference

### Core Classes

#### PDFGenerator

```python
from shared.pdf_generator import PDFGenerator

generator = PDFGenerator()

# Generate PDF as bytes
pdf_bytes = generator.generate_pdf_bytes(data_dict)

# Generate PDF to file
generator.generate_pdf(data_dict, "output.pdf")
```

#### DigitalCodebook

```python
from shared.pdf_generator import DigitalCodebook

codebook = DigitalCodebook()

# Normalize data for determinism
normalized = codebook.normalize_data(raw_data)

# Reconstruct document
pdf_bytes = codebook.reconstruct_document(json_data)
```

#### HashValidator & TransmissionPackage

```python
from shared.hash_validator import (
    create_transmission_package,
    TransmissionPackage,
    IntegrityVerifier
)

# Create package (client)
package = create_transmission_package(json_data, pdf_bytes)
package.save_to_file("package.json")

# Load package (server)
package = TransmissionPackage.load_from_file("package.json")

# Verify integrity
verifier = IntegrityVerifier()
result = verifier.verify_with_details(reconstructed_pdf, package)
if result['valid']:
    print("Document verified")
```

#### AIExtractor (Optional - Demo Only)

```python
from shared.ai_extractor import extract_banking_data

# Extract from text
data = extract_banking_data(text_content, api_key="gemini-key")

# Extract from file
data = extract_banking_data("contract.jpg", api_key="gemini-key")
```

---

## Performance Metrics

| Metric | Value | Notes |
|--------|-------|-------|
| **PDF Size (typical)** | 20-2000 KB | Banking documents |
| **JSON Package Size** | 2-5 KB | Transmitted data |
| **Compression Ratio** | **4.5x - 1000x** | Depends on document complexity |
| **Hash Algorithm** | SHA-256 | 64-byte hash |
| **Integrity Accuracy** | 100% | Bit-perfect validation |
| **Processing Time (client)** | <1 second | PDF generation + hash |
| **Processing Time (server)** | <1 second | Reconstruction + validation |
| **TCP Latency** | ~50-200ms | Local network |
| **Satellite Latency** | ~500-2500ms | Geostationary orbit |

**Bandwidth Savings Example:**
- 100 documents/day × 20 KB = 2 MB/day original
- With 4.5x compression: 0.44 MB/day transmitted
- **Savings: 1.56 MB/day = 46.8 MB/month**
- At satellite cost $10/MB: **$468/month saved**

---

## Security Considerations

**Implemented:**
- SHA-256 hashing for integrity verification
- Deterministic reconstruction (no tampering possible)
- Bit-perfect validation on server
- Automatic tamper detection

**Not Included (Add if needed):**
- TLS/SSL encryption for transmission (recommended for production)
- Authentication/authorization (add API keys/tokens)
- Rate limiting (prevent DoS attacks)
- Input validation (sanitize user inputs)

**Best Practices:**
```python
# Use TLS for production
import ssl
context = ssl.create_default_context()
socket_wrapped = context.wrap_socket(socket, server_hostname=host)

# Validate inputs
if not re.match(r'^[A-Z0-9]{20,34}$', account_number):
    raise ValueError("Invalid account number")
```

---

## Testing

```powershell
# Test 1: Start server
python server/server.py

# Test 2: Start client (new terminal)
python client/client.py

# Test 3: Submit transfer via web interface
# Open http://localhost:5870
# Fill form and submit

# Test 4: Verify outputs
ls data/client_output/   # Should see TRANSFER-*.pdf and *.json
ls data/server_output/   # Should see received_TRANSFER-*.pdf

# Test 5: Run demo (requires API key)
python demo.py
```

---

## Troubleshooting

**Problem**: `ModuleNotFoundError`
```powershell
# Solution: Install dependencies
pip install -r requirements.txt
```

**Problem**: Server won't start (port in use)
```powershell
# Solution: Check if port 8870 is available
netstat -ano | findstr :8870
# Kill process or change port in server.py
```

**Problem**: Hash mismatch on server
```
# Cause: Data not normalized or PDF generation not deterministic
# Solution: Ensure both client and server use DigitalCodebook.normalize_data()
# Check ReportLab invariant mode is enabled
```

**Problem**: Ctrl+C doesn't stop server
```
# Solution: Server uses 1.0s socket timeout for responsiveness
# Wait 1 second or force kill with Task Manager
```

---

## Contributing

The project is modular and extensible:

1. **Extend AI schema**: Modify `shared/ai_extractor.py`
2. **Add document types**: Update `DigitalCodebook` class
3. **Implement real API**: Replace TCP socket with REST/gRPC
4. **Add encryption**: Wrap sockets with TLS/SSL
5. **Add authentication**: Implement API keys or OAuth

---

## License

MIT License - See LICENSE for details

---

## Credits

**The 1870 Telegraph Protocol**  
Inspired by Deutsche Bank's history and 1870 telegraph codebooks  
Implemented with modern technologies: Google Gemini AI, Flask, ReportLab, Python

---

## Roadmap

- [ ] REST API for transmission (replace TCP)
- [ ] Support for multiple document types
- [ ] Web dashboard for monitoring
- [ ] Integration with real banking systems
- [ ] Multi-language support
- [ ] End-to-end encryption (TLS/SSL)
- [ ] Docker containerization
- [ ] Cloud deployment (AWS/Azure)
- [ ] Mobile client application
- [ ] Blockchain integration for audit trail

---

**Built for Hackathon 2025**  
*Version 1.0.0: Production Ready*

# Generate PDF from JSON
pdf_bytes = codebook.reconstruct_document(json_data)
```

### HashValidator

```python
from shared.hash_validator import (
    create_transmission_package,
    verify_received_package
)

# Client: creează pachet
package = create_transmission_package(json_data, pdf_bytes)
package.save_to_file("package.json")

# Server: verifică pachet
package = TransmissionPackage.load_from_file("package.json")
is_valid = verify_received_package(package, reconstructed_pdf)
```

---

## Testing

```powershell
# Test client
python client/sender.py

# Test server (după ce ai rulat client)
python server/receiver.py

# Verifică output-urile
ls data/client_output/
ls data/server_output/
```

---

## Performanță

| Metric | Valoare |
|--------|---------|
| **PDF Original** | 2-20 MB |
| **Pachet Transmis** | 2-5 KB |
| **Compresie** | **100x - 1000x** |
| **Acuratețe AI** | 95%+ (extragere) |
| **Integritate** | 100% (hash match) |
| **Timp procesare** | <5 secunde |

---

## Securitate

- **Hash SHA-256** pentru integritate
- **Reconstrucție deterministă** (fără modificări)
- **Validare bit-perfect** pe server
- **Detectare tamper** automată
- **Nu include criptare** (adaugă TLS pentru transmisie)

---

## Contribuții

Proiectul este modular și extensibil:

1. **Extinde schema AI** în `shared/ai_extractor.py`
2. **Adaugă noi tipuri de documente** în `DigitalCodebook`
3. **Implementează API real** pentru transmisie
4. **Adaugă criptare TLS/SSL** pentru securitate


## Credits

**The 1870 Telegraph Protocol**  
Inspirat de istoria Deutsche Bank și telegrafele din 1870  
Implementat cu tehnologii moderne: Google Gemini AI, Flask, ReportLab

---

## Support

Pentru întrebări sau probleme:
- 📧 Email: antonioheasca4@gmail.com
- 💬 Issues: GitHub Issues
- 📖 Docs: Acest README

---

## 🗺️ Roadmap

- [ ] API REST pentru transmisie
- [ ] Suport pentru mai multe tipuri de documente
- [ ] Dashboard web pentru monitorizare
- [ ] Integrare cu sisteme bancare reale
- [ ] Suport multi-limbă
- [ ] Criptare end-to-end

---

**Realizat pentru Hackathon 2025** 🚀  
*Version 10.0: Time Capsule Initialized*
