"""
PDF Generator for SmartInvoice AI
Generates professional, enterprise-grade styled PDF invoices using ReportLab.
"""

import io
import os
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, HRFlowable
)
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER

def generate_invoice_pdf(invoice_data: dict, output_path: str = None) -> bytes:
    """
    Generate a high-quality PDF invoice.
    
    :param invoice_data: Dictionary containing:
        - invoice_number: str
        - created_at: str
        - customer_name: str
        - customer_email: str
        - items: list of dicts with [service_name, quantity, unit_price, subtotal]
        - subtotal: float
        - discount_amount: float
        - tax_amount: float
        - total_amount: float
        - status: str ('PAID', 'PENDING', etc.)
        - notes: str (optional)
    :param output_path: Optional file path to write the PDF to.
    :return: PDF content as bytes.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        output_path if output_path else buffer,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    story = []
    styles = getSampleStyleSheet()

    # Custom Palette
    PRIMARY = colors.HexColor("#4F46E5")     # Indigo
    PRIMARY_DARK = colors.HexColor("#312E81")# Deep Navy
    SECONDARY = colors.HexColor("#0F172A")   # Slate 900
    TEXT_MUTED = colors.HexColor("#64748B")  # Slate 500
    BG_LIGHT = colors.HexColor("#F8FAFC")    # Slate 50
    BG_ROW_ALT = colors.HexColor("#F1F5F9")  # Slate 100
    BORDER_COLOR = colors.HexColor("#E2E8F0")# Slate 200
    SUCCESS_COLOR = colors.HexColor("#059669")# Emerald 600
    WARNING_COLOR = colors.HexColor("#D97706")# Amber 600

    # Custom Typography Styles
    style_logo = ParagraphStyle(
        'Logo',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=PRIMARY
    )
    
    style_tagline = ParagraphStyle(
        'Tagline',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=TEXT_MUTED
    )

    style_inv_title = ParagraphStyle(
        'InvoiceTitle',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        alignment=TA_RIGHT,
        textColor=SECONDARY
    )

    style_inv_meta = ParagraphStyle(
        'InvoiceMeta',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        alignment=TA_RIGHT,
        textColor=TEXT_MUTED
    )

    style_section_heading = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading3'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=14,
        textColor=PRIMARY_DARK,
        textTransform='uppercase'
    )

    style_body = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=SECONDARY
    )

    style_body_bold = ParagraphStyle(
        'BodyDarkBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=13,
        textColor=SECONDARY
    )

    style_table_header = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        textColor=colors.white
    )

    style_table_header_r = ParagraphStyle(
        'TableHeaderR',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        alignment=TA_RIGHT,
        textColor=colors.white
    )

    style_table_cell = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=SECONDARY
    )

    style_table_cell_r = ParagraphStyle(
        'TableCellR',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        alignment=TA_RIGHT,
        textColor=SECONDARY
    )

    style_notes = ParagraphStyle(
        'NotesStyle',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8.5,
        leading=12,
        textColor=TEXT_MUTED
    )

    # 1. Header Banner (Brand Left, Invoice Info Right)
    inv_num = invoice_data.get("invoice_number", "INV-2026-0000")
    inv_date = invoice_data.get("created_at", datetime.now().strftime("%Y-%m-%d %H:%M"))
    status = invoice_data.get("status", "PAID").upper()
    status_color = SUCCESS_COLOR if status == "PAID" else WARNING_COLOR

    header_left = [
        Paragraph("⚡ SmartInvoice AI", style_logo),
        Spacer(1, 2),
        Paragraph("Next-Gen Intelligent Billing & Automation", style_tagline),
        Paragraph("support@smartinvoice.ai &bull; www.smartinvoice.ai", style_tagline),
    ]

    header_right = [
        Paragraph("INVOICE", style_inv_title),
        Spacer(1, 2),
        Paragraph(f"<b>Invoice #:</b> {inv_num}", style_inv_meta),
        Paragraph(f"<b>Date:</b> {inv_date}", style_inv_meta),
        Paragraph(f"<b>Status:</b> <font color='{status_color.hexval()}'><b>{status}</b></font>", style_inv_meta),
    ]

    header_table = Table([[header_left, header_right]], colWidths=[3.2 * inch, 4.3 * inch])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 14))

    # Divider
    story.append(HRFlowable(width="100%", thickness=1.5, color=PRIMARY, spaceBefore=2, spaceAfter=14))

    # 2. Bill To & Bill From Section
    cust_name = invoice_data.get("customer_name", "Valued Client")
    cust_email = invoice_data.get("customer_email", "client@example.com")

    bill_to = [
        Paragraph("BILLED TO", style_section_heading),
        Spacer(1, 4),
        Paragraph(f"<b>{cust_name}</b>", style_body_bold),
        Paragraph(f"{cust_email}", style_body),
        Paragraph("Payment Method: Wire / Stripe / UPI", style_notes),
    ]

    bill_from = [
        Paragraph("PAYABLE TO", style_section_heading),
        Spacer(1, 4),
        Paragraph("<b>SmartInvoice AI Technologies Inc.</b>", style_body_bold),
        Paragraph("100 Innovation Boulevard, Suite 500", style_body),
        Paragraph("Silicon Valley, CA 94025 &bull; USA", style_body),
        Paragraph("GSTIN/Tax ID: US94025-AI-INV01", style_notes),
    ]

    info_table = Table([[bill_to, bill_from]], colWidths=[3.75 * inch, 3.75 * inch])
    info_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BACKGROUND', (0, 0), (-1, -1), BG_LIGHT),
        ('BOX', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 16))

    # 3. Itemized Table
    raw_items = invoice_data.get("items", [])
    table_data = [
        [
            Paragraph("#", style_table_header),
            Paragraph("Service Description", style_table_header),
            Paragraph("Qty", style_table_header_r),
            Paragraph("Unit Price", style_table_header_r),
            Paragraph("Amount", style_table_header_r)
        ]
    ]

    for idx, item in enumerate(raw_items, start=1):
        s_name = item.get("service_name") or item.get("matched_service_name") or "Service Item"
        qty = float(item.get("quantity", 1))
        unit_price = float(item.get("unit_price", 0.0))
        subtot = float(item.get("subtotal", qty * unit_price))
        
        # Display nicely formatted qty (integer if whole)
        qty_str = f"{int(qty)}" if qty.is_integer() else f"{qty:.2f}"
        
        table_data.append([
            Paragraph(str(idx), style_table_cell),
            Paragraph(s_name, style_table_cell),
            Paragraph(qty_str, style_table_cell_r),
            Paragraph(f"${unit_price:,.2f}", style_table_cell_r),
            Paragraph(f"${subtot:,.2f}", style_table_cell_r)
        ])

    # If empty items
    if len(raw_items) == 0:
        table_data.append([
            Paragraph("1", style_table_cell),
            Paragraph("General Consulting / Services", style_table_cell),
            Paragraph("1", style_table_cell_r),
            Paragraph(f"${invoice_data.get('subtotal', 0.0):,.2f}", style_table_cell_r),
            Paragraph(f"${invoice_data.get('subtotal', 0.0):,.2f}", style_table_cell_r)
        ])

    items_table = Table(table_data, colWidths=[0.4 * inch, 3.8 * inch, 0.8 * inch, 1.2 * inch, 1.3 * inch])
    
    t_style = [
        ('BACKGROUND', (0, 0), (-1, 0), PRIMARY),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
    ]
    
    # Alternate row styling
    for r in range(1, len(table_data)):
        if r % 2 == 0:
            t_style.append(('BACKGROUND', (0, r), (-1, r), BG_ROW_ALT))
            
    items_table.setStyle(TableStyle(t_style))
    story.append(items_table)
    story.append(Spacer(1, 14))

    # 4. Calculation Summary Block
    subtotal = float(invoice_data.get("subtotal", 0.0))
    discount = float(invoice_data.get("discount_amount", 0.0))
    tax = float(invoice_data.get("tax_amount", 0.0))
    total = float(invoice_data.get("total_amount", subtotal - discount + tax))

    summary_rows = [
        [Paragraph("Subtotal:", style_table_cell), Paragraph(f"${subtotal:,.2f}", style_table_cell_r)],
    ]
    if discount > 0:
        summary_rows.append([Paragraph("Discount:", style_table_cell), Paragraph(f"-${discount:,.2f}", style_table_cell_r)])
    summary_rows.append([Paragraph("Tax (18% GST/VAT):", style_table_cell), Paragraph(f"${tax:,.2f}", style_table_cell_r)])
    summary_rows.append([
        Paragraph("<b>Total Amount Due:</b>", style_body_bold),
        Paragraph(f"<b><font size='11' color='{PRIMARY_DARK.hexval()}'>${total:,.2f}</font></b>", style_table_cell_r)
    ])

    summary_table = Table(summary_rows, colWidths=[1.8 * inch, 1.4 * inch])
    summary_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('LINEBELOW', (0, -2), (-1, -2), 1, BORDER_COLOR),
        ('BACKGROUND', (0, -1), (-1, -1), BG_LIGHT),
        ('BOX', (0, -1), (-1, -1), 1, PRIMARY),
    ]))

    # Place summary aligned to the right side
    notes_text = invoice_data.get("notes", "Payment is due within 15 days of invoice date. Thank you for choosing SmartInvoice AI!")
    left_notes = [
        Paragraph("<b>TERMS & CONDITIONS</b>", style_section_heading),
        Spacer(1, 3),
        Paragraph(notes_text, style_notes),
        Spacer(1, 4),
        Paragraph("For wire transfers: ACME Bank &bull; Routing: 121000358 &bull; Account: 9876543210", style_notes)
    ]

    total_block = Table([[left_notes, summary_table]], colWidths=[4.3 * inch, 3.2 * inch])
    total_block.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ]))

    story.append(KeepTogether([total_block]))
    story.append(Spacer(1, 24))

    # 5. Footer
    footer_text = Paragraph(
        "<font color='#94A3B8'>SmartInvoice AI Automated Billing Engine &bull; Generated seamlessly via Dual-Agent AI Pipeline &bull; Page 1 of 1</font>",
        ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, alignment=TA_CENTER)
    )
    story.append(footer_text)

    # Build PDF
    doc.build(story)
    
    if output_path:
        with open(output_path, "rb") as f:
            pdf_bytes = f.read()
        return pdf_bytes
    else:
        pdf_bytes = buffer.getvalue()
        buffer.close()
        return pdf_bytes

if __name__ == "__main__":
    sample_data = {
        "invoice_number": "INV-2026-1001",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "customer_name": "Acme Innovations Inc.",
        "customer_email": "billing@acmeinnovations.com",
        "items": [
            {"service_name": "Website UI/UX Design", "quantity": 1, "unit_price": 500.0, "subtotal": 500.0},
            {"service_name": "Python Backend API Development", "quantity": 2, "unit_price": 400.0, "subtotal": 800.0},
            {"service_name": "Monthly Cloud Hosting & Maintenance", "quantity": 3, "unit_price": 50.0, "subtotal": 150.0}
        ],
        "subtotal": 1450.0,
        "discount_amount": 50.0,
        "tax_amount": 252.0,
        "total_amount": 1652.0,
        "status": "PAID",
        "notes": "Standard Net-30 enterprise contract terms."
    }
    test_file = os.path.join(os.path.dirname(__file__), "test_invoice.pdf")
    generate_invoice_pdf(sample_data, test_file)
    print(f"Generated sample PDF at {test_file}, size: {os.path.getsize(test_file)} bytes")
