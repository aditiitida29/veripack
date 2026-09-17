import json
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.inspection import Inspection
from app.models.user import User
from app.api.deps import get_current_user
from app.reports.pdf_generator import generate_inspection_pdf

router = APIRouter(prefix="/reports", tags=["Inspection PDF Reports"])

@router.get("/{id}/pdf")
def get_or_generate_report_pdf(
    id: int,
    download: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    insp = db.query(Inspection).filter(Inspection.id == id).first()
    if not insp:
        raise HTTPException(status_code=404, detail="Inspection not found")

    try:
        rule_results = json.loads(insp.rule_results) if insp.rule_results else []
        image_paths = json.loads(insp.image_paths) if insp.image_paths else []
    except Exception:
        rule_results, image_paths = [], []

    summary = {
        "pass_count": insp.pass_count,
        "fail_count": insp.fail_count,
        "warning_count": insp.warning_count,
        "confidence_score": insp.confidence_score
    }

    product_data = {
        "name": insp.product.name,
        "category": insp.product.category,
        "is_imported": insp.product.is_imported,
        "brand": insp.product.brand
    }

    inspector_data = {
        "full_name": insp.inspector.full_name,
        "department": insp.inspector.department,
        "badge_number": insp.inspector.badge_number
    }

    inspection_data = {
        "created_at": str(insp.created_at)
    }

    pdf_file_path = generate_inspection_pdf(
        inspection_code=insp.inspection_code,
        inspection_data=inspection_data,
        product_data=product_data,
        inspector_data=inspector_data,
        image_paths=image_paths,
        rule_results=rule_results,
        overall_status=insp.status,
        summary=summary,
        inspector_remarks=insp.inspector_remarks or ""
    )

    insp.pdf_path = pdf_file_path
    db.commit()

    filename = f"{insp.inspection_code}_Compliance_Report.pdf"
    disposition = "attachment" if download else "inline"

    return FileResponse(
        path=pdf_file_path,
        media_type="application/pdf",
        filename=filename,
        headers={"Content-Disposition": f'{disposition}; filename="{filename}"'}
    )
