from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.product import Product
from app.models.inspection import Inspection
from app.schemas.product import ProductOut
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/products", tags=["Product Catalog"])

@router.get("")
def list_products(
    search: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    limit: int = Query(50, le=100),
    offset: int = Query(0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Product)
    if category:
        query = query.filter(Product.category == category)
    if search:
        s = f"%{search}%"
        query = query.filter((Product.name.ilike(s)) | (Product.brand.ilike(s)))
    
    products = query.order_by(Product.created_at.desc()).offset(offset).limit(limit).all()
    
    result = []
    for p in products:
        insp_count = len(p.inspections)
        latest_status = p.inspections[-1].status if p.inspections else "NOT_INSPECTED"
        result.append({
            "id": p.id,
            "name": p.name,
            "brand": p.brand,
            "category": p.category,
            "barcode": p.barcode,
            "is_imported": p.is_imported,
            "created_at": p.created_at,
            "inspections_count": insp_count,
            "latest_status": latest_status
        })
    return result

@router.get("/{id}")
def get_product_detail(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    p = db.query(Product).filter(Product.id == id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Product not found")
    
    inspections = []
    for i in p.inspections:
        inspections.append({
            "id": i.id,
            "inspection_code": i.inspection_code,
            "status": i.status,
            "pass_count": i.pass_count,
            "fail_count": i.fail_count,
            "warning_count": i.warning_count,
            "confidence_score": i.confidence_score,
            "created_at": i.created_at
        })
        
    return {
        "id": p.id,
        "name": p.name,
        "brand": p.brand,
        "category": p.category,
        "barcode": p.barcode,
        "is_imported": p.is_imported,
        "description": p.description,
        "created_at": p.created_at,
        "inspections": inspections
    }
