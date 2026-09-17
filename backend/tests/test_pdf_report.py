from pathlib import Path
from app.reports.pdf_generator import generate_inspection_pdf

def test_pdf_generation():
    pdf_path = generate_inspection_pdf(
        inspection_code="TEST-INSP-001",
        inspection_data={"created_at": "2026-09-17T22:00:00"},
        product_data={"name": "Test Salt Pack", "category": "FOOD_BEVERAGE", "is_imported": False},
        inspector_data={"full_name": "Rajesh Sharma", "department": "DoCA Enforcement"},
        image_paths=[],
        rule_results=[
            {
                "rule_name": "Maximum Retail Price (MRP)",
                "field": "mrp",
                "status": "PASS",
                "legal_reference": "Rule 6(1)(e)",
                "message": "MRP compliant: ₹ 28.00 (inclusive of all taxes).",
                "evidence": "MRP Rs. 28.00 (Incl. of all taxes)"
            }
        ],
        overall_status="COMPLIANT",
        summary={"pass_count": 1, "fail_count": 0, "warning_count": 0, "confidence_score": 100},
        inspector_remarks="Test Remarks"
    )

    path_obj = Path(pdf_path)
    assert path_obj.exists()
    assert path_obj.stat().st_size > 1000
    # Clean up test pdf
    path_obj.unlink()
