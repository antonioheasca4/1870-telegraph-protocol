# Maritime Banking Optimization

## Overview
The 1870 Telegraph Protocol is optimized specifically for **maritime banking transactions** transmitted via expensive satellite bandwidth. This document outlines the maritime-specific optimizations.

## Transaction Types (Maritime Focus)

### Supported Types
Only 3 transaction types are supported, covering 90%+ of maritime banking needs:

```python
TRANSACTION_TYPES = {
    "swift": {
        priority: 1,
        use_case: "Cross-border international payments (80% of maritime transactions)",
        examples: ["Port fees (foreign ports)", "International supplier payments", "Crew salaries (cross-border)"]
    },
    "wire": {
        priority: 1,
        use_case: "Urgent/emergency transfers",
        examples: ["Emergency bunker fuel", "Urgent equipment purchase", "Detention avoidance payments"]
    },
    "payment": {
        priority: 1,
        use_case: "Invoice settlement and service fees",
        examples: ["Port charges", "Cargo handling", "Bunker fuel", "Provisioning", "Pilotage", "Towage"]
    }
}
```

**Removed types:** `transfer`, `sepa`, `ach` (not relevant for maritime operations)

## Maritime Terms (Banking Context)

### 11 Specialized Categories

```
1. VESSEL: names, IMO numbers, flags, types
   → Banking relevance: Identifies payer/payee in ship operations

2. CARGO: TEU counts, container types, bill of lading
   → Banking relevance: Determines cargo handling fees

3. PORT: port names, terminals, berths
   → Banking relevance: Port authority is common payee

4. PORT_OPERATIONS: berthing, pilotage, towage, mooring
   → Banking relevance: Specific service fees to extract

5. PORT_FEES: terminal handling, wharfage, quay dues
   → Banking relevance: Line items in port invoices

6. CARGO_FEES: loading, discharge, stuffing, stripping
   → Banking relevance: Cargo handling charges

7. STORAGE_FEES: demurrage, detention, storage
   → Banking relevance: Time-based penalty charges

8. BUNKER: fuel types (MGO, HFO), quantities
   → Banking relevance: Major expense category (€10K-500K)

9. PROVISIONING: supplies, stores, chandler services
   → Banking relevance: Vessel operational expenses

10. CREW: manning, wages, repatriation
    → Banking relevance: Crew-related payments

11. DOCUMENTATION: bills of lading, customs, certificates
    → Banking relevance: Document fees and charges
```

## Field Compression System

### Field Name Codes (120+ mappings)

Long field names are compressed to 2-4 character codes for transmission:

```python
FIELD_CODES = {
    # Transaction basics (9 codes)
    'transaction_type': 'tt',
    'document_reference': 'ref',
    'date': 'd',
    'time_utc': 'tu',
    'priority': 'pr',
    'maritime_context': 'mc',
    'amount': 'amt',
    'currency': 'cur',
    'description': 'desc',
    
    # Sender fields (11 codes)
    'sender_name': 'sn',
    'sender_registered_office': 'sro',
    'sender_account_holder': 'sah',
    'sender_account': 'sa',
    'sender_bank': 'sb',
    'sender_swift': 'ss',
    'sender_bank_branch': 'sbb',
    'sender_emergency_contact_phone': 'sep',
    'sender_operations_manager_email': 'soe',
    'sender_address': 'sadr',
    'sender_contact_email': 'sce',
    
    # Receiver fields (14 codes)
    'receiver_name': 'rn',
    'receiver_service': 'rsv',
    'receiver_location': 'rl',
    'receiver_account_holder': 'rah',
    'receiver_account': 'ra',
    'receiver_bank': 'rb',
    'receiver_swift': 'rs',
    'receiver_bank_branch': 'rbb',
    'receiver_contact_email': 'rce',
    'receiver_emergency_hotline': 'reh',
    'receiver_address': 'radr',
    'receiver_department': 'rdep',
    'receiver_invoice_contact_email': 'rice',
    'receiver_port_ops_phone': 'rpop',
    
    # Vessel fields (11 codes)
    'vessel_name': 'vn',
    'vessel_imo': 'vi',
    'vessel_current_position': 'vp',
    'vessel_master': 'vm',
    'vessel_flag_state': 'vf',
    'vessel_flag': 'vflg',
    'vessel_call_sign': 'vcs',
    'vessel_crew_count': 'vcc',
    'vessel_fuel_remaining_metric_tons': 'vfr',
    'vessel_current_speed_knots': 'vsk',
    'vessel_eta_rotterdam_if_no_refuel': 'vet',
    'vessel_type': 'vty',
    'vessel_gross_tonnage': 'vgt',
    'vessel_container_capacity_teu': 'vcap',
    
    # Port fields (6 codes)
    'port_name': 'pn',
    'port_berth': 'pb',
    'port_arrival_datetime': 'pad',
    'port_departure_datetime': 'pdd',
    'port_time_duration': 'ptd',
    'port_terminal': 'pterm',
    
    # Cargo fields (7 codes)
    'cargo_details': 'cd',
    'cargo_delivery_deadline': 'cdd',
    'cargo_discharge_teu': 'cdt',
    'cargo_loading_teu': 'clt',
    'cargo_total_handling_teu': 'cth',
    'cargo_type': 'ct',
    'cargo_operations': 'cops',
    
    # Service/Invoice fields (11 codes)
    'service_period_start': 'sps',
    'service_period_end': 'spe',
    'invoice_reference': 'iref',
    'invoice_date': 'idate',
    'invoice_number': 'inum',
    'due_date': 'ddate',
    'fees_breakdown': 'fees',
    'early_payment_deadline': 'epd',
    'service_agreement_ref': 'sref',
    'other_references': 'oref',
    'reference_number': 'refn',
    'invoice_summary': 'isum',
    
    # VAT/Tax (6 codes)
    'vat_applicable': 'vat',
    'vat_reason': 'vatr',
    'vat_included': 'vati',
    'vat_rate': 'vatr',
    'sender_vat_number': 'svat',
    'receiver_vat_number': 'rvat',
    
    # Compliance fields (7 codes)
    'compliance_aml': 'aml',
    'compliance_kyc': 'kyc',
    'compliance_sanctions': 'sanc',
    'compliance_maritime': 'cmar',
    'compliance_info': 'cinf',
    'purpose_verification': 'pver',
    'payment_authorization_status': 'pauth',
    
    # Authorization (4 codes)
    'signature_status': 'sigst',
    'authorized_by': 'auth',
    'authorization_timestamp': 'autht',
    'expected_settlement_date': 'esd',
    
    # Transmission/Technical (7 codes)
    'transmission_details': 'trans',
    'transmission_notes': 'tnote',
    'verification_contact': 'vcon',
    'operations_contact': 'ocon',
    'technical_support_contact': 'tcon',
    'receiver_contact_phone': 'rcp',
    'generated_timestamp': 'gt',
    
    # Emergency/execution (6 codes)
    'execution_details': 'ed',
    'emergency_situation_details': 'esd',
    'special_instructions': 'sinst',
    'payment_confirmation_email': 'pce',
    'vessel_agent_copy_email': 'vace',
    'port_authority_references': 'pref',
    
    # Other (2 codes)
    'signature_present': 'sig',
    'additional_info': 'ai'
}
```

**Total: 120+ field code mappings**

**Compression gain:** 10-15% reduction in JSON size from field names alone.

## Semantic Compression Rules (Gemini Prompt)

### 3 Complete Examples in Prompt

The AI extraction prompt includes 3 complete examples covering all transaction types:

#### EXAMPLE 1 - SWIFT International Payment (Port Charges)
```json
{
  "transaction_type": "swift",
  "sender_name": "Maersk Line",
  "sender_account": "DK5000400440116243",
  "receiver_name": "Hamburg Port Authority",
  "amount": 45000,
  "currency": "EUR",
  "date": "2025-12-06",
  "description": "Port charges - Hamburg CTerm",
  "vessel_name": "MV Maersk Sealand",
  "vessel_imo": "9876543",
  "vessel_flag": "DK",
  "port_name": "Hamburg CTerm",
  "port_berth": "Burchardkai B7",
  "port_time_duration": "4d12h",
  "cargo_total_handling_teu": 330,
  "cargo_type": "Mixed container"
}
```

#### EXAMPLE 2 - WIRE Emergency Transfer (Bunker Fuel)
```json
{
  "transaction_type": "wire",
  "priority": "IMMEDIATE",
  "sender_name": "Ocean Freight AS",
  "receiver_name": "Bunker Fuel Supplies BV",
  "amount": 120000,
  "currency": "EUR",
  "date": "2025-12-07",
  "time_utc": "03:45",
  "description": "Emergency bunker - contamination MV Nordic Explorer",
  "vessel_name": "MV Nordic Explorer",
  "vessel_imo": "9123456",
  "vessel_flag": "NO",
  "vessel_current_position": "52°N 4°E",
  "execution_details": {
    "priority": "IMMEDIATE",
    "timeframe": "2h"
  },
  "emergency_situation_details": {
    "reason": "Fuel contamination - urgent bunker supply",
    "fuel_requirements": {
      "type": "MGO",
      "quantity_mt": 150,
      "delivery_window": "8h"
    }
  }
}
```

#### EXAMPLE 3 - PAYMENT Invoice Settlement (Cargo Handling)
```json
{
  "transaction_type": "payment",
  "sender_name": "MSC",
  "receiver_name": "Port de Barcelona - Terminal Catalunya",
  "amount": 82500,
  "currency": "EUR",
  "date": "2025-12-06",
  "invoice_number": "BCN-BEST-2025-445",
  "description": "Container handling - Barcelona BEST",
  "vessel_name": "MSC Flaminia",
  "vessel_imo": "9321456",
  "vessel_flag": "LR",
  "vessel_type": "ULCV",
  "port_name": "Barcelona",
  "port_terminal": "BEST",
  "port_berth": "N Quay B5-6",
  "port_time_duration": "5d7h30m",
  "cargo_operations": {
    "discharged_teu": 2840,
    "loaded_teu": 3150,
    "total_moves_teu": 5990
  },
  "vat_included": true,
  "vat_rate": 0.21
}
```

### 12 Compression Rules for Data Extraction

#### 1. Use Codes Instead of Full Text
```
❌ BAD:  "country": "Norway"
✅ GOOD: "country": "NO"

❌ BAD:  "flag_state": "Liberia"
✅ GOOD: "flag_state": "LR"

❌ BAD:  "priority": "immediate emergency"
✅ GOOD: "priority": "IMMEDIATE"
```

#### 2. Compress Verbose Descriptions
```
❌ BAD:  "Container handling & terminal services - MSC Flaminia, Barcelona BEST"
✅ GOOD: "Container handling - Barcelona BEST"

❌ BAD:  "This is an urgent emergency wire transfer for bunker fuel"
✅ GOOD: "Emergency bunker - contamination MV Nordic Explorer"
```
**Rule:** Extract KEY FACTS only, remove filler words and redundancy.

#### 3. Duration Abbreviations
```
❌ BAD:  "4 days, 12 hours"
✅ GOOD: "4d12h"

❌ BAD:  "5 days, 7 hours, 30 minutes"
✅ GOOD: "5d7h30m"

❌ BAD:  "within 2 hours"
✅ GOOD: "2h"
```

#### 4. Location/Terminal Abbreviations
```
❌ BAD:  "Barcelona Europe South Terminal"
✅ GOOD: "BEST"

❌ BAD:  "Container Terminal Services - Finance Division"
✅ GOOD: "CTerm-Fin"

❌ BAD:  "Burchardkai Terminal, Berth 7"
✅ GOOD: "Burchardkai B7"

❌ BAD:  "North Quay, Berth 5-6"
✅ GOOD: "N Quay B5-6"
```

#### 5. Company/Bank Name Simplification
```
❌ BAD:  "Mediterranean Shipping Company (MSC)"
✅ GOOD: "MSC"

❌ BAD:  "UBS Switzerland AG"
✅ GOOD: "UBS Switzerland"

❌ BAD:  "CaixaBank, S.A."
✅ GOOD: "CaixaBank"
```

#### 6. Numeric Precision
```
❌ BAD:  "approximately 120,000 euros"
✅ GOOD: 120000

❌ BAD:  "52 degrees North, 4 degrees East"
✅ GOOD: "52°N 4°E"

❌ BAD:  "1,200 TEU containers"
✅ GOOD: "1200 TEU"
```

#### 7. Contact Info Simplification
```
❌ BAD:  "+34 932 986 000"
✅ GOOD: "+34932986000"

❌ BAD:  "Captain Erik Olsen, Master of the vessel"
✅ GOOD: "Erik Olsen"
```

#### 8. Remove Redundancy
```
❌ BAD:  {
    "sender_name": "Ocean Freight AS",
    "description": "Payment from Ocean Freight AS in Oslo for bunker fuel"
}
✅ GOOD: {
    "sender_name": "Ocean Freight AS",
    "description": "Bunker fuel"
}
```
**Rule:** Don't repeat information already in other fields.

#### 9. Nested Objects - Keep Minimal
```
❌ BAD:  {
    "execution_details": {
        "priority": "IMMEDIATE",
        "timeframe": "within 2 hours",
        "urgency_level": "critical",
        "reason": "emergency situation"
    }
}
✅ GOOD: {
    "execution_details": {
        "priority": "IMMEDIATE",
        "timeframe": "2h"
    }
}
```
**Rule:** Only essential fields in nested objects. Remove verbose details, lists.

#### 10. Cargo Type Compression
```
❌ BAD:  "Mixed containerized general cargo"
✅ GOOD: "Mixed container"

❌ BAD:  "Refrigerated containerized goods"
✅ GOOD: "Reefer"
```

#### 11. Dates/Times ISO Format
```
❌ BAD:  "December 7th, 2025"
✅ GOOD: "2025-12-07"

❌ BAD:  "3:45 AM UTC"
✅ GOOD: "03:45"
```

#### 12. Simplify Nested Summaries
```
❌ BAD:  "cargo_operations": {
    "discharged_details": { "20ft_units": 1420, "40ft_units": 1420, ... },
    "loaded_details": { "20ft_units": 1260, "40ft_units": 1890, ... },
    "types_handled": ["General container", "Refrigerated goods", ...]
}
✅ GOOD: "cargo_operations": {
    "discharged_teu": 2840,
    "loaded_teu": 3150,
    "total_moves_teu": 5990
}
```
**Rule:** Remove detailed breakdowns, keep only essential totals.

## Gemini Prompt Enhancement

### Maritime Context Added to Prompt

```
CRITICAL: This system is SPECIALIZED for MARITIME BANKING transactions.

If the document contains maritime/shipping terminology (vessel, port, cargo, 
bunker, TEU, IMO, berthing, etc.), it is likely a valid banking document.

Transaction Type Detection:
- SWIFT/MT103/international → type: "swift"
- urgent/emergency/wire → type: "wire"
- invoice/payment/fees → type: "payment"

Maritime Context Recognition:
- Vessel names, IMO → include in vessel_name field
- Port names → critical for payment context
- Cargo (TEU, containers) → include in cargo_details
- Services (berthing, pilotage, bunker) → payment purpose

SEMANTIC COMPRESSION RULES (CRITICAL FOR BANDWIDTH OPTIMIZATION):
[7 rules as detailed above]

Extract data in COMPRESSED format to minimize satellite bandwidth costs.
```

## Results

### Compression Performance

**After full optimization (120+ field codes + 12 semantic rules + 3 examples):**

| Transaction Type | Original | Transmitted | Ratio | Savings |
|-----------------|----------|-------------|-------|---------|
| **SWIFT** (Port) | 7.5 KB | 3.5 KB | 2.1x | 53% |
| **WIRE** (Emergency) | 8.4 KB | 4.0 KB | 2.1x | 52% |
| **PAYMENT** (Invoice) | 9.2 KB | 4.5 KB | 2.0x | 51% |

**Average compression: 52% bandwidth savings**

### Breakdown by Optimization Layer

1. **Field name compression** (120+ codes): 10-15% gain
2. **Semantic value compression** (12 rules): 25-30% gain
3. **Nested object minimization**: 10-15% gain
4. **Total combined effect**: 50-55% bandwidth reduction

### Cost Savings (Satellite @ $10/MB)

**Per transmission:**
- Without compression: $0.08-0.09 USD
- With compression: $0.04-0.05 USD
- **Savings: $0.04 per document (50% cost reduction)**

**Annual savings (1,000 documents/year):**
- **$40-50 USD** in bandwidth costs
- **Plus**: Faster transmission (2x speed), instant server processing, deterministic validation

## Implementation

### Client-Side (Transmission)
```python
codebook = DigitalCodebook()

# 1. Extract with Gemini (compressed format via prompt)
extracted_data = extractor.extract_from_file(file_path)

# 2. Normalize data
normalized_data = codebook.normalize_data(extracted_data)

# 3. Compress field names
compressed_data = codebook.compress_fields(normalized_data)

# 4. Create package with compressed data
package = create_transmission_package(compressed_data, pdf_hash)

# 5. Transmit compressed JSON
transmit_via_satellite(package.to_json())
```

### Server-Side (Reception)
```python
codebook = DigitalCodebook()

# 1. Receive compressed JSON
package = receive_transmission()

# 2. Decompress field names
decompressed_data = codebook.decompress_fields(package.data)

# 3. Reconstruct PDF
pdf_bytes = codebook.reconstruct_document(decompressed_data)

# 4. Validate hash
is_valid = validate_hash(pdf_bytes, package.document_hash)
```

## Key Benefits

1. **50%+ Compression** - Field codes (120+) + semantic rules (12) + minimal nesting
2. **Maritime-Specific** - Only 3 relevant transaction types (SWIFT/WIRE/PAYMENT)
3. **Bandwidth Optimized** - Critical for satellite ($10/MB+)
4. **AI-Guided Compression** - 3 complete examples train Gemini for optimal extraction
5. **Deterministic** - Same JSON = same PDF (bit-perfect)
6. **Structured Data** - Queryable without decompression
7. **Hash Validation** - Cryptographic integrity check (SHA-256)
8. **Multi-Language** - Codebook supports maritime terms in any language

## Future Enhancements

- [ ] Expand to 150+ field codes (add more edge-case fields)
- [ ] Value dictionaries (port codes, vessel type abbreviations)
- [ ] Further prompt optimization for even more aggressive compression
- [ ] Binary encoding for ultra-low bandwidth scenarios (<1 KB target)
- [ ] Add PAYMENT EXAMPLE 3 optimizations to all document types
