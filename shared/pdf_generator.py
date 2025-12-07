"""
PDF Generator Module
Generates deterministic PDFs from JSON using ReportLab.
Same JSON = same PDF (bit-perfect reproduction).
"""

import os
from typing import Dict, Any, Optional
from pathlib import Path
from datetime import datetime
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

# CRITICAL: Set invariant mode for deterministic reproducibility
# This eliminates timestamps and random IDs from PDF
import reportlab.rl_config
reportlab.rl_config.invariant = 1


class PDFGenerator:
    """Generates deterministic PDFs from JSON data."""
    
    def __init__(self):
        """
        Initializes PDF generator.
        """
        # Stiluri pentru PDF
        self.styles = getSampleStyleSheet()
        
        # Custom styles
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#0066cc'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        self.section_style = ParagraphStyle(
            'SectionTitle',
            parent=self.styles['Heading2'],
            fontSize=12,
            textColor=colors.HexColor('#0066cc'),
            spaceAfter=10,
            spaceBefore=15,
            fontName='Helvetica-Bold',
            borderColor=colors.HexColor('#0066cc'),
            borderWidth=0,
            borderPadding=5,
            backColor=colors.HexColor('#f0f0f0')
        )
        
        self.normal_style = ParagraphStyle(
            'CustomNormal',
            parent=self.styles['Normal'],
            fontSize=10,
            leading=14,
            wordWrap='LTR',  # Enable word wrapping
            splitLongWords=True  # Split long words if needed
        )
    
    def _create_header(self, data: Dict[str, Any]) -> list:
        """Creates document header."""
        elements = []
        
        # Title
        title = f"BANKING DOCUMENT - {data.get('transaction_type', 'N/A').upper()}"
        elements.append(Paragraph(title, self.title_style))
        
        # Reference info
        ref_data = [
            ['Reference:', data.get('reference_number', 'N/A')],
            ['Date:', data.get('date', 'N/A')]
        ]
        ref_table = Table(ref_data, colWidths=[4*cm, 12*cm])
        ref_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.grey),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ]))
        elements.append(ref_table)
        elements.append(Spacer(1, 0.5*cm))
        
        return elements
    
    def _create_section(self, title: str, data: list) -> list:
        """Creates a data section."""
        elements = []
        
        elements.append(Paragraph(title, self.section_style))
        
        # Create table with data - use None for second column to allow flexible width
        table = Table(data, colWidths=[6*cm, None])
        table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#333333')),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 0.3*cm))
        
        return elements
    
    def _create_amount_box(self, amount: float, currency: str) -> list:
        """Creates amount display box."""
        elements = []
        
        # Convert amount to float if it's a string
        amount_value = float(amount) if isinstance(amount, str) else amount
        
        amount_data = [
            [f"{currency}"],
            [f"{amount_value:,.2f}"]
        ]
        
        amount_table = Table(amount_data, colWidths=[16*cm])
        amount_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#e6f2ff')),
            ('BOX', (0, 0), (-1, -1), 2, colors.HexColor('#0066cc')),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, 1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('FONTSIZE', (0, 1), (-1, 1), 24),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#0066cc')),
            ('TEXTCOLOR', (0, 1), (-1, 1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 15),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
        ]))
        
        elements.append(amount_table)
        elements.append(Spacer(1, 0.5*cm))
        
        return elements
    
    def generate_pdf_bytes(
        self, 
        data: Dict[str, Any]
    ) -> bytes:
        """
        Generates PDF as bytes (without saving to disk).
        
        Args:
            data: Dictionary with AI-extracted data (MUST be already normalized!)
            
        Returns:
            Bytes with generated PDF
        """
        # IMPORTANT: Do NOT generate dynamic timestamp here!
        # Timestamp must come from normalized data
        # to ensure deterministic reproducibility
        
        # Create PDF in memory
        buffer = BytesIO()
        
        # CRITICAL: Set deterministic metadata pentru reproducibilitate
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm,
            title=f"Banking Document",
            author="1870 Telegraph Protocol",
            subject="Banking Transaction",
            creator="Digital Codebook v1.0.0",
            producer="ReportLab PDF Library"
        )
        
        # Build content
        elements = []
        
        # Header
        elements.extend(self._create_header(data))
        
        # Define fields to skip (technical/internal fields)
        skip_fields = {
            'generated_timestamp', 'reference_number', 'signature_status', 
            'date', 'signature_present', 'additional_info'
        }
        
        # Group fields by prefix
        sender_fields = {}
        receiver_fields = {}
        other_fields = {}
        
        for key, value in sorted(data.items()):
            if key in skip_fields or not value:
                continue
            
            if key.startswith('sender_'):
                sender_fields[key] = value
            elif key.startswith('receiver_'):
                receiver_fields[key] = value
            else:
                other_fields[key] = value
        
        # Sender section - dynamic from JSON
        if sender_fields:
            sender_data = []
            for field, value in sender_fields.items():
                label = field.replace('sender_', '').replace('_', ' ').title()
                if isinstance(value, dict):
                    # Format dict nicely: key: value on separate lines
                    value = '<br/>'.join([f'{k.replace("_", " ").title()}: {v}' for k, v in value.items()])
                elif isinstance(value, list):
                    # Format list nicely: bullet points
                    value = '<br/>'.join([f'• {item}' for item in value])
                sender_data.append([f'{label}:', Paragraph(str(value), self.normal_style)])
            elements.extend(self._create_section('SENDER INFORMATION', sender_data))
        
        # Receiver section - dynamic from JSON
        if receiver_fields:
            receiver_data = []
            for field, value in receiver_fields.items():
                label = field.replace('receiver_', '').replace('_', ' ').title()
                if isinstance(value, dict):
                    # Format dict nicely: key: value on separate lines
                    value = '<br/>'.join([f'{k.replace("_", " ").title()}: {v}' for k, v in value.items()])
                elif isinstance(value, list):
                    # Format list nicely: bullet points
                    value = '<br/>'.join([f'• {item}' for item in value])
                receiver_data.append([f'{label}:', Paragraph(str(value), self.normal_style)])
            elements.extend(self._create_section('RECEIVER INFORMATION', receiver_data))
        
        # Amount box
        if data.get('amount'):
            elements.extend(self._create_amount_box(
                data.get('amount', 0),
                data.get('currency', 'EUR')
            ))
        
        # All other fields - organized dynamically
        for field, value in other_fields.items():
            if field in ['amount', 'currency']:
                continue  # Already shown in amount box
            
            # Handle special types
            if isinstance(value, list):
                # Lists (line_items, cargo_manifest, etc.)
                elements.append(Paragraph(field.replace('_', ' ').title(), self.section_style))
                for idx, item in enumerate(value, 1):
                    if isinstance(item, dict):
                        item_text = f"<b>Item {idx}:</b><br/>"
                        for k, v in item.items():
                            item_text += f"{k.replace('_', ' ').title()}: {v}<br/>"
                        elements.append(Paragraph(item_text, self.normal_style))
                        elements.append(Spacer(1, 0.2*cm))
                    else:
                        elements.append(Paragraph(f"• {item}", self.normal_style))
                elements.append(Spacer(1, 0.3*cm))
            
            elif isinstance(value, dict):
                # Dictionaries (bank_details, emergency_transmission_details, etc.)
                dict_data = []
                for k, v in value.items():
                    label = k.replace('_', ' ').title()
                    # Format nested values properly
                    if isinstance(v, dict):
                        # Nested dict - format as key: value pairs
                        formatted_v = '<br/>'.join([f'{nk.replace("_", " ").title()}: {nv}' for nk, nv in v.items()])
                        dict_data.append([f'{label}:', Paragraph(formatted_v, self.normal_style)])
                    elif isinstance(v, list):
                        # Nested list - format as bullet points
                        formatted_v = '<br/>'.join([f'• {item}' for item in v])
                        dict_data.append([f'{label}:', Paragraph(formatted_v, self.normal_style)])
                    else:
                        # Simple value
                        dict_data.append([f'{label}:', Paragraph(str(v), self.normal_style)])
                elements.extend(self._create_section(field.replace('_', ' ').title(), dict_data))
            
            else:
                # Simple fields - group them
                label = field.replace('_', ' ').title()
                if not hasattr(self, '_other_data'):
                    self._other_data = []
                self._other_data.append([f'{label}:', Paragraph(str(value), self.normal_style)])
        
        # Add grouped "other" fields
        if hasattr(self, '_other_data'):
            elements.extend(self._create_section('TRANSACTION DETAILS', self._other_data))
            delattr(self, '_other_data')
        
        # Additional info (if exists as string)
        if data.get('additional_info') and isinstance(data.get('additional_info'), str):
            elements.extend(self._create_section('ADDITIONAL INFORMATION', [
                ['Note:', Paragraph(data['additional_info'], self.normal_style)]
            ]))
        
        # Signature
        if data.get('signature_present'):
            elements.append(Spacer(1, 1*cm))
            sig_text = " Electronically verified signature"
            elements.append(Paragraph(sig_text, self.normal_style))
        
        # Footer
        elements.append(Spacer(1, 1*cm))
        footer_style = ParagraphStyle(
            'Footer',
            parent=self.styles['Normal'],
            fontSize=8,
            textColor=colors.grey,
            alignment=TA_CENTER
        )
        footer_text = """Document generated according to 1870 Telegraph Protocol - Semantic Compression System<br/>
        All information extracted and validated according to Digital Codebook"""
        elements.append(Paragraph(footer_text, footer_style))
        
        # Timestamp
        timestamp_style = ParagraphStyle(
            'Timestamp',
            parent=self.styles['Normal'],
            fontSize=7,
            textColor=colors.lightgrey,
            alignment=TA_RIGHT
        )
        elements.append(Spacer(1, 0.3*cm))
        elements.append(Paragraph(f"Generated: {data['generated_timestamp']}", timestamp_style))
        
        # Build PDF
        doc.build(elements)
        
        # Get bytes
        pdf_bytes = buffer.getvalue()
        buffer.close()
        
        return pdf_bytes
    
    def generate_pdf(
        self, 
        data: Dict[str, Any], 
        output_path: str
    ) -> str:
        """
        Generates deterministic PDF from JSON data.
        
        Args:
            data: Dictionary with AI-extracted data
            output_path: Path where PDF will be saved
            
        Returns:
            Path to generated PDF file
        """
        # Generate PDF bytes
        pdf_bytes = self.generate_pdf_bytes(data)
        
        # Save PDF
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'wb') as f:
            f.write(pdf_bytes)
        
        return str(output_path)


class DigitalCodebook:
    """
    Digital Codebook - Set of rules for deterministic PDF reconstruction.
    Ensures that same JSON produces same output on client and server.
    Includes field compression for bandwidth optimization.
    """
    
    # Codebook version (for synchronization between client and server)
    VERSION = "1.0.0"
    
    # Field compression mapping (long field names → short codes)
    FIELD_CODES = {
        # Transaction basics
        'transaction_type': 'tt',
        'document_reference': 'ref',
        'date': 'd',
        'time_utc': 'tu',
        'priority': 'pr',
        'maritime_context': 'mc',
        'amount': 'amt',
        'currency': 'cur',
        'description': 'desc',
        
        # Sender fields
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
        
        # Receiver fields
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
        
        # Vessel fields
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
        
        # Port fields
        'port_name': 'pn',
        'port_berth': 'pb',
        'port_arrival_datetime': 'pad',
        'port_departure_datetime': 'pdd',
        'port_time_duration': 'ptd',
        
        # Cargo fields
        'cargo_details': 'cd',
        'cargo_delivery_deadline': 'cdd',
        'cargo_discharge_teu': 'cdt',
        'cargo_loading_teu': 'clt',
        'cargo_total_handling_teu': 'cth',
        'cargo_type': 'ct',
        
        # Service/Invoice fields
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
        
        # VAT/Tax
        'vat_applicable': 'vat',
        'vat_reason': 'vatr',
        'vat_included': 'vati',
        'vat_rate': 'vatr',
        'sender_vat_number': 'svat',
        'receiver_vat_number': 'rvat',
        
        # Vessel extended
        'vessel_type': 'vty',
        'vessel_gross_tonnage': 'vgt',
        'vessel_container_capacity_teu': 'vcap',
        
        # Port extended
        'port_terminal': 'pterm',
        
        # Cargo operations
        'cargo_operations': 'cops',
        
        # Invoice summary
        'invoice_summary': 'isum',
        
        # Compliance fields
        'compliance_aml': 'aml',
        'compliance_kyc': 'kyc',
        'compliance_sanctions': 'sanc',
        'compliance_maritime': 'cmar',
        'compliance_info': 'cinf',
        'purpose_verification': 'pver',
        
        # Payment/Authorization
        'payment_authorization_status': 'pauth',
        'expected_settlement_date': 'esd',
        'receiver_contact_phone': 'rcp',
        
        # Authorization
        'signature_status': 'sigst',
        'authorized_by': 'auth',
        'authorization_timestamp': 'autht',
        
        # Transmission/Technical
        'transmission_details': 'trans',
        'transmission_notes': 'tnote',
        'verification_contact': 'vcon',
        'operations_contact': 'ocon',
        'technical_support_contact': 'tcon',
        
        # Emergency/execution
        'execution_details': 'ed',
        'emergency_situation_details': 'esd',
        'special_instructions': 'sinst',
        'payment_confirmation_email': 'pce',
        'vessel_agent_copy_email': 'vace',
        
        # References
        'port_authority_references': 'pref',
        
        # Technical
        'generated_timestamp': 'gt',
        'signature_present': 'sig',
        'additional_info': 'ai'
    }
    
    # Reverse mapping for decompression
    CODE_TO_FIELD = {v: k for k, v in FIELD_CODES.items()}
    
    def __init__(self):
        """
        Initializes Digital Codebook.
        """
        self.pdf_generator = PDFGenerator()
    
    def compress_fields(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compresses field names using short codes.
        
        Args:
            data: Data with full field names
            
        Returns:
            Data with compressed field names
        """
        compressed = {}
        for key, value in data.items():
            # Use short code if available, otherwise keep original
            short_key = self.FIELD_CODES.get(key, key)
            
            # Recursively compress nested dicts
            if isinstance(value, dict):
                compressed[short_key] = self.compress_fields(value)
            elif isinstance(value, list):
                # Compress list items if they're dicts
                compressed[short_key] = [
                    self.compress_fields(item) if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                compressed[short_key] = value
        
        return compressed
    
    def decompress_fields(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Decompresses field names from short codes.
        
        Args:
            data: Data with compressed field names
            
        Returns:
            Data with full field names
        """
        decompressed = {}
        for key, value in data.items():
            # Expand short code if it exists, otherwise keep original
            full_key = self.CODE_TO_FIELD.get(key, key)
            
            # Recursively decompress nested dicts
            if isinstance(value, dict):
                decompressed[full_key] = self.decompress_fields(value)
            elif isinstance(value, list):
                # Decompress list items if they're dicts
                decompressed[full_key] = [
                    self.decompress_fields(item) if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                decompressed[full_key] = value
        
        return decompressed
    
    def normalize_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalizes data to ensure reproducibility.
        Sorts keys, formats dates, etc.
        
        Args:
            data: Raw data
            
        Returns:
            Normalized data (decompressed for processing)
        """
        # First decompress if data contains short codes
        normalized = self.decompress_fields(data.copy())
        
        # Ensure we have required fields
        if 'transaction_type' not in normalized:
            normalized['transaction_type'] = 'unknown'
        
        if 'date' not in normalized:
            normalized['date'] = datetime.utcnow().strftime('%Y-%m-%d')
        
        # IMPORTANT: Fixed timestamp for deterministic reproducibility
        # Use document date as basis for timestamp
        if 'generated_timestamp' not in normalized:
            # Deterministic timestamp based on document date
            doc_date = normalized.get('date', '2025-01-01')
            normalized['generated_timestamp'] = f"{doc_date} 00:00:00 UTC"
        
        # Sort additional_info for consistency
        if 'additional_info' in normalized and isinstance(normalized['additional_info'], dict):
            normalized['additional_info'] = dict(sorted(normalized['additional_info'].items()))
        
        return normalized
    
    def reconstruct_document(
        self, 
        json_data: Dict[str, Any], 
        output_path: Optional[str] = None
    ) -> bytes:
        """
        Reconstructs PDF document from JSON according to codebook.
        This function produces same output on client and server.
        
        Args:
            json_data: Extracted and normalized data
            output_path: Path for saving (optional)
            
        Returns:
            Bytes with generated PDF
        """
        # Normalize data
        normalized_data = self.normalize_data(json_data)
        
        # Generate PDF
        if output_path:
            self.pdf_generator.generate_pdf(normalized_data, output_path)
            with open(output_path, 'rb') as f:
                return f.read()
        else:
            return self.pdf_generator.generate_pdf_bytes(normalized_data)
# Helper function for quick use
def generate_banking_pdf(
    json_data: Dict[str, Any],
    output_path: str
) -> str:
    """
    Helper function for quick generation of banking PDF.
    
    Args:
        json_data: AI-extracted data
        output_path: Where to save PDF
        
    Returns:
        Path to generated PDF
    """
    codebook = DigitalCodebook()
    pdf_bytes = codebook.reconstruct_document(json_data, output_path)
    return output_path


if __name__ == "__main__":
    # Usage example
    print(f"Digital Codebook v{DigitalCodebook.VERSION} - Ready")
    print("Usage:")
    print("  from shared.pdf_generator import DigitalCodebook")
    print("  codebook = DigitalCodebook()")
    print("  pdf_bytes = codebook.reconstruct_document(json_data)")
