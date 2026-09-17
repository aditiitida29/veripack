import os
from pathlib import Path
from typing import Dict, Any, List
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image as RLImage,
    KeepTogether,
    HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from app.config import UPLOAD_DIR

REPORTS_DIR = UPLOAD_DIR / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

def generate_inspection_pdf(
    inspection_code: str,
    inspection_data: Dict[str, Any],
    product_data: Dict[str, Any],
    inspector_data: Dict[str, Any],
    image_paths: List[str],
    rule_results: List[Dict[str, Any]],
    overall_status: str,
    summary: Dict[str, Any],
    inspector_remarks: str = ""
) -> str:
    """
    Generates a professional DoCA inspection PDF report.
    Returns the absolute path to the generated PDF file.
    """
    pdf_filename = f"{inspection_code}.pdf"
    pdf_path = REPORTS_DIR / pdf_filename

    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=18,
        alignment=1, # Center
        textColor=colors.HexColor('#0F2942')
    )
    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        alignment=1,
        textColor=colors.HexColor('#4A5568')
    )
    section_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=14,
        textColor=colors.HexColor('#0F2942'),
        spaceAfter=6
    )
    normal_style = ParagraphStyle(
        'NormalSmall',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor('#2D3748')
    )
    bold_style = ParagraphStyle(
        'BoldSmall',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor('#1A202C')
    )
    disclaimer_style = ParagraphStyle(
        'DisclaimerText',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor('#718096')
    )

    story = []

    # 1. Government Header Banner
    story.append(Paragraph("GOVERNMENT OF INDIA", subtitle_style))
    story.append(Paragraph("MINISTRY OF CONSUMER AFFAIRS, FOOD & PUBLIC DISTRIBUTION", subtitle_style))
    story.append(Paragraph("DEPARTMENT OF CONSUMER AFFAIRS — LEGAL METROLOGY DIVISION", subtitle_style))
    story.append(Spacer(1, 4))
    story.append(Paragraph("STATUTORY PACKAGED COMMODITIES COMPLIANCE REPORT", title_style))
    story.append(Paragraph("Issued under Legal Metrology Act, 2009 & Legal Metrology (Packaged Commodities) Rules, 2011", subtitle_style))
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#0F2942'), spaceAfter=10))

    # 2. Inspection & Product Metadata Table
    status_color = colors.HexColor('#16A34A') if overall_status == "COMPLIANT" else (
        colors.HexColor('#D97706') if overall_status == "REVIEW_REQUIRED" else colors.HexColor('#DC2626')
    )
    status_text = f"<b>STATUS: {overall_status.replace('_', ' ')}</b>"

    meta_table_data = [
        [
            Paragraph(f"<b>Inspection Code:</b> {inspection_code}", normal_style),
            Paragraph(f"<b>Date:</b> {inspection_data.get('created_at', '2026-09-17')[:19]}", normal_style)
        ],
        [
            Paragraph(f"<b>Product Name:</b> {product_data.get('name', 'Packaged Commodity')}", normal_style),
            Paragraph(f"<b>Category:</b> {product_data.get('category', 'GENERAL')}", normal_style)
        ],
        [
            Paragraph(f"<b>Inspector:</b> {inspector_data.get('full_name', 'Enforcement Officer')}", normal_style),
            Paragraph(f"<b>Badge / Dept:</b> {inspector_data.get('department', 'DoCA Enforcement')}", normal_style)
        ],
        [
            Paragraph(f"<b>Imported Commodity:</b> {'YES' if product_data.get('is_imported') else 'NO'}", normal_style),
            Paragraph(f"<font color='{status_color.hexval()}'>{status_text}</font>", normal_style)
        ]
    ]

    meta_table = Table(meta_table_data, colWidths=[260, 260])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8FAFC')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#CBD5E1')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 12))

    # 3. Compliance Summary Banner
    summary_data = [
        [
            Paragraph(f"<b>Passed Declarations:</b> {summary.get('pass_count', 0)}", normal_style),
            Paragraph(f"<b>Violations (Fail):</b> {summary.get('fail_count', 0)}", normal_style),
            Paragraph(f"<b>Review / Warnings:</b> {summary.get('warning_count', 0)}", normal_style),
            Paragraph(f"<b>Compliance Score:</b> {summary.get('confidence_score', 0)}%", normal_style)
        ]
    ]
    summary_table = Table(summary_data, colWidths=[130, 130, 130, 130])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#EEF2F6')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#CBD5E1')),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 12))

    # 4. Detailed Statutory Rule Audit Table
    story.append(Paragraph("STATUTORY DECLARATION AUDIT BREAKDOWN", section_style))

    rule_table_data = [
        [
            Paragraph("<b>Rule & Field</b>", bold_style),
            Paragraph("<b>Statutory Reference</b>", bold_style),
            Paragraph("<b>Status</b>", bold_style),
            Paragraph("<b>Finding & Evidence</b>", bold_style)
        ]
    ]

    for r in rule_results:
        st = r.get("status", "PASS")
        st_color = "#16A34A" if st == "PASS" else ("#D97706" if st == "WARNING" else ("#DC2626" if st == "FAIL" else "#6B7280"))
        
        status_cell = Paragraph(f"<font color='{st_color}'><b>{st}</b></font>", normal_style)
        rule_cell = Paragraph(f"<b>{r.get('rule_name')}</b><br/><font color='#64748B'>{r.get('field')}</font>", normal_style)
        ref_cell = Paragraph(r.get('legal_reference', ''), normal_style)
        
        finding_text = f"{r.get('message', '')}"
        if r.get('evidence'):
            finding_text += f"<br/><i>Observed:</i> <font color='#1E293B'>{r.get('evidence')}</font>"
        finding_cell = Paragraph(finding_text, normal_style)

        rule_table_data.append([rule_cell, ref_cell, status_cell, finding_cell])

    rule_table = Table(rule_table_data, colWidths=[120, 110, 60, 230])
    rule_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E2E8F0')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#CBD5E1')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(rule_table)
    story.append(Spacer(1, 14))

    # 5. Inspector Remarks
    story.append(Paragraph("ENFORCEMENT OFFICER REMARKS & ACTIONS", section_style))
    remarks_content = inspector_remarks or "Label scanned and evaluated digitally via VeriPack enforcement module. Findings recorded for statutory records."
    story.append(Paragraph(f"<b>Remarks:</b> {remarks_content}", normal_style))
    story.append(Spacer(1, 14))

    # 6. Attached Photographic Evidence
    if image_paths:
        first_img = image_paths[0]
        abs_img_path = Path(first_img)
        if not abs_img_path.is_absolute():
            abs_img_path = UPLOAD_DIR.parent / first_img

        if abs_img_path.exists():
            try:
                story.append(Paragraph("ATTACHED PHOTOGRAPHIC EVIDENCE", section_style))
                rl_img = RLImage(str(abs_img_path), width=3.0*inch, height=2.2*inch)
                img_table = Table([[rl_img]], colWidths=[520])
                img_table.setStyle(TableStyle([
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
                    ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8FAFC')),
                    ('TOPPADDING', (0, 0), (-1, -1), 6),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ]))
                story.append(img_table)
                story.append(Spacer(1, 12))
            except Exception:
                pass

    # 7. Signature & Statutory Disclaimer
    sig_data = [
        [
            Paragraph("<b>Verified By:</b><br/>Enforcement Officer / Inspector<br/>Legal Metrology Department", normal_style),
            Paragraph("<b>Officer Seal & Signature:</b><br/><br/>___________________________", normal_style)
        ]
    ]
    sig_table = Table(sig_data, colWidths=[260, 260])
    sig_table.setStyle(TableStyle([
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(sig_table)
    story.append(Spacer(1, 10))

    disclaimer_text = (
        "<b>STATUTORY DISCLAIMER:</b> This inspection report is a computer-generated preliminary assessment produced by "
        "the VeriPack AI-assisted enforcement decision support system under the Legal Metrology (Packaged Commodities) Rules, 2011. "
        "This preliminary report does not constitute an automatic or binding judicial verdict. "
        "Any penal action, seizure, or notice under Section 15 or Section 36 of the Legal Metrology Act, 2009 "
        "must be preceded by physical verification by an authorized enforcement officer."
    )
    story.append(Paragraph(disclaimer_text, disclaimer_style))

    doc.build(story)
    return str(pdf_path)
