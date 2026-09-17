import json
import uuid
import datetime
import shutil
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.config import UPLOAD_DIR, DEMO_ASSETS_DIR
from app.models.user import User, UserRole
from app.models.product import Product, ProductCategory
from app.models.inspection import Inspection, ComplianceStatus
from app.schemas.inspection import InspectionOut, InspectionListItem, InspectionUpdateRemarks
from app.api.deps import get_current_user
from app.ocr.ocr_engine import run_ocr_with_boxes
from app.ocr.declaration_parser import parse_declarations_from_ocr
from app.rules.rule_engine import evaluate_compliance

router = APIRouter(prefix="/scans", tags=["Product Scans & Inspections"])

IMAGES_DIR = UPLOAD_DIR / "images"
IMAGES_DIR.mkdir(parents=True, exist_ok=True)

@router.post("/analyze")
async def analyze_product(
    files: Optional[List[UploadFile]] = File(None),
    demo_key: Optional[str] = Form(None),
    product_name: Optional[str] = Form(None),
    category: str = Form("GENERAL"),
    is_imported: bool = Form(False),
    barcode: Optional[str] = Form(None),
    inspector_remarks: Optional[str] = Form(""),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    saved_rel_paths: List[str] = []
    primary_abs_path: Optional[Path] = None
    is_demo = False

    if demo_key:
        demo_map = {
            "compliant_salt": ("demo_compliant_salt.png", "Tata Pure Refined Iodised Salt", "FOOD_BEVERAGE", False),
            "missing_mrp_snack": ("demo_missing_mrp_snack.png", "Royal Crunch Butter Cookies", "FOOD_BEVERAGE", False),
            "ambiguous_qty": ("demo_ambiguous_qty.png", "Natural Energy Protein Mix", "FOOD_BEVERAGE", False),
            "imported_earbuds": ("demo_imported_earbuds.png", "Aero Wireless Buds", "ELECTRONICS", True),
            "warnings_spice": ("demo_warnings_spice.png", "Spice Delight Garam Masala", "FOOD_BEVERAGE", False),
        }
        if demo_key in demo_map:
            fname, d_name, d_cat, d_imp = demo_map[demo_key]
            src_file = DEMO_ASSETS_DIR / fname
            if src_file.exists():
                dest_fname = f"demo_{uuid.uuid4().hex[:8]}_{fname}"
                dest_path = IMAGES_DIR / dest_fname
                shutil.copyfile(src_file, dest_path)
                saved_rel_paths.append(f"uploads/images/{dest_fname}")
                primary_abs_path = dest_path
                is_demo = True
                if not product_name:
                    product_name = d_name
                category = d_cat
                is_imported = d_imp

    if files:
        for f in files:
            if f.filename:
                ext = Path(f.filename).suffix.lower()
                if ext not in [".jpg", ".jpeg", ".png", ".webp"]:
                    continue
                unique_name = f"scan_{uuid.uuid4().hex[:10]}{ext}"
                dest_path = IMAGES_DIR / unique_name
                content = await f.read()
                dest_path.write_bytes(content)
                saved_rel_paths.append(f"uploads/images/{unique_name}")
                if primary_abs_path is None:
                    primary_abs_path = dest_path

    if not primary_abs_path or not primary_abs_path.exists():
        raise HTTPException(
            status_code=400,
            detail="No valid image provided. Please upload an image or select a demo scenario."
        )

    ocr_result = run_ocr_with_boxes(str(primary_abs_path))
    
    manual_info = {"product_name": product_name} if product_name else None
    extracted_declarations = parse_declarations_from_ocr(ocr_result, manual_info)
    
    detected_pname = extracted_declarations.get("product_name", {}).get("value")
    final_pname = product_name or detected_pname or "Packaged Commodity"

    compliance_evaluation = evaluate_compliance(
        extracted_declarations=extracted_declarations,
        product_category=category,
        is_imported=is_imported,
        db=db
    )

    summary = compliance_evaluation["summary"]
    rule_results = compliance_evaluation["rule_results"]
    overall_status = compliance_evaluation["overall_status"]

    product = db.query(Product).filter(Product.name == final_pname).first()
    if not product:
        product = Product(
            name=final_pname,
            brand=extracted_declarations.get("manufacturer", {}).get("name") or "Various Brands",
            category=category,
            barcode=barcode,
            is_imported=is_imported
        )
        db.add(product)
        db.commit()
        db.refresh(product)

    rand_code = uuid.uuid4().hex[:5].upper()
    insp_code = f"INSP-2026-{rand_code}"

    bounding_boxes = []
    for r in rule_results:
        bb = r.get("bounding_box")
        if bb:
            bounding_boxes.append({
                "rule_code": r["rule_code"],
                "field": r["field"],
                "status": r["status"],
                "box": bb,
                "label": r["rule_name"]
            })

    new_inspection = Inspection(
        inspection_code=insp_code,
        product_id=product.id,
        inspector_id=current_user.id,
        status=overall_status,
        pass_count=summary["pass_count"],
        fail_count=summary["fail_count"],
        warning_count=summary["warning_count"],
        confidence_score=summary["confidence_score"],
        extracted_fields=json.dumps(extracted_declarations),
        rule_results=json.dumps(rule_results),
        bounding_boxes=json.dumps(bounding_boxes),
        raw_ocr_text=ocr_result.get("raw_text", ""),
        image_paths=json.dumps(saved_rel_paths),
        inspector_remarks=inspector_remarks,
        is_demo=is_demo,
        created_at=datetime.datetime.utcnow()
    )
    db.add(new_inspection)
    db.commit()
    db.refresh(new_inspection)

    return {
        "id": new_inspection.id,
        "inspection_code": new_inspection.inspection_code,
        "product_id": product.id,
        "product_name": product.name,
        "category": product.category,
        "is_imported": product.is_imported,
        "status": new_inspection.status,
        "pass_count": new_inspection.pass_count,
        "fail_count": new_inspection.fail_count,
        "warning_count": new_inspection.warning_count,
        "confidence_score": new_inspection.confidence_score,
        "extracted_fields": extracted_declarations,
        "rule_results": rule_results,
        "bounding_boxes": bounding_boxes,
        "raw_ocr_text": new_inspection.raw_ocr_text,
        "image_paths": saved_rel_paths,
        "font_metrics": ocr_result.get("font_metrics", {}),
        "inspector_remarks": new_inspection.inspector_remarks,
        "is_demo": new_inspection.is_demo,
        "created_at": new_inspection.created_at,
        "disclaimer": compliance_evaluation.get("disclaimer")
    }

@router.get("", response_model=List[InspectionListItem])
def list_inspections(
    status: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    limit: int = Query(50, le=100),
    offset: int = Query(0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Inspection).join(Product).join(User)

    # For CONSUMER role, show their own scans and demo scans
    if current_user.role == UserRole.CONSUMER:
        query = query.filter(
            (Inspection.inspector_id == current_user.id) | (Inspection.is_demo == True)
        )

    if status:
        query = query.filter(Inspection.status == status)
    if category:
        query = query.filter(Product.category == category)
    if search:
        s = f"%{search}%"
        query = query.filter(
            (Inspection.inspection_code.ilike(s)) |
            (Product.name.ilike(s)) |
            (Product.brand.ilike(s))
        )

    query = query.order_by(Inspection.created_at.desc())
    inspections = query.offset(offset).limit(limit).all()

    items = []
    for insp in inspections:
        img_list = []
        try:
            img_list = json.loads(insp.image_paths) if insp.image_paths else []
        except Exception:
            img_list = []

        items.append(InspectionListItem(
            id=insp.id,
            inspection_code=insp.inspection_code,
            product_id=insp.product.id,
            product_name=insp.product.name,
            category=insp.product.category,
            inspector_id=insp.inspector.id,
            inspector_name=insp.inspector.full_name,
            status=insp.status,
            pass_count=insp.pass_count,
            fail_count=insp.fail_count,
            warning_count=insp.warning_count,
            confidence_score=insp.confidence_score,
            image_paths=img_list,
            created_at=insp.created_at,
            is_demo=insp.is_demo
        ))
    return items

@router.get("/{id}")
def get_inspection_detail(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    insp = db.query(Inspection).filter(Inspection.id == id).first()
    if not insp:
        raise HTTPException(status_code=404, detail="Inspection not found")

    try:
        extracted = json.loads(insp.extracted_fields) if insp.extracted_fields else {}
        rule_res = json.loads(insp.rule_results) if insp.rule_results else []
        bbs = json.loads(insp.bounding_boxes) if insp.bounding_boxes else []
        img_paths = json.loads(insp.image_paths) if insp.image_paths else []
    except Exception:
        extracted, rule_res, bbs, img_paths = {}, [], [], []

    return {
        "id": insp.id,
        "inspection_code": insp.inspection_code,
        "product_id": insp.product.id,
        "product": {
            "id": insp.product.id,
            "name": insp.product.name,
            "brand": insp.product.brand,
            "category": insp.product.category,
            "barcode": insp.product.barcode,
            "is_imported": insp.product.is_imported
        },
        "inspector": {
            "id": insp.inspector.id,
            "full_name": insp.inspector.full_name,
            "email": insp.inspector.email,
            "department": insp.inspector.department
        },
        "status": insp.status,
        "pass_count": insp.pass_count,
        "fail_count": insp.fail_count,
        "warning_count": insp.warning_count,
        "confidence_score": insp.confidence_score,
        "extracted_fields": extracted,
        "rule_results": rule_res,
        "bounding_boxes": bbs,
        "raw_ocr_text": insp.raw_ocr_text,
        "image_paths": img_paths,
        "inspector_remarks": insp.inspector_remarks,
        "is_demo": insp.is_demo,
        "pdf_path": insp.pdf_path,
        "created_at": insp.created_at
    }

@router.patch("/{id}/remarks")
def update_inspection_remarks(
    id: int,
    body: InspectionUpdateRemarks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    insp = db.query(Inspection).filter(Inspection.id == id).first()
    if not insp:
        raise HTTPException(status_code=404, detail="Inspection not found")
    
    insp.inspector_remarks = body.inspector_remarks
    db.commit()
    return {"message": "Remarks updated successfully", "remarks": insp.inspector_remarks}
