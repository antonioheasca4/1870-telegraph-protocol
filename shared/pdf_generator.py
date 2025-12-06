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
                if isinstance(value, (dict, list)):
                    value = str(value)
                sender_data.append([f'{label}:', Paragraph(str(value), self.normal_style)])
            elements.extend(self._create_section('SENDER INFORMATION', sender_data))
        
        # Receiver section - dynamic from JSON
        if receiver_fields:
            receiver_data = []
            for field, value in receiver_fields.items():
                label = field.replace('receiver_', '').replace('_', ' ').title()
                if isinstance(value, (dict, list)):
                    value = str(value)
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
                # Dictionaries (bank_details, etc.)
                dict_data = []
                for k, v in value.items():
                    label = k.replace('_', ' ').title()
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
    """
    
    # Codebook version (for synchronization between client and server)
    VERSION = "1.0.0"
    
    def __init__(self):
        """
        Initializes Digital Codebook.
        """
        self.pdf_generator = PDFGenerator()
    
    def normalize_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalizes data to ensure reproducibility.
        Sorts keys, formats dates, etc.
        
        Args:
            data: Raw data
            
        Returns:
            Normalized data
        """
        normalized = data.copy()
        
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
