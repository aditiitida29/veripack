import json
from collections import Counter
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.inspection import Inspection, ComplianceStatus
from app.models.product import Product
from app.models.user import User
from app.api.deps import get_current_user

router = APIRouter(prefix="/dashboard", tags=["Enforcement Analytics & Dashboard"])

@router.get("/stats")
def get_dashboard_statistics(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    inspections = db.query(Inspection).order_by(Inspection.created_at.desc()).all()
    total_scans = len(inspections)
    
    compliant_cnt = sum(1 for i in inspections if i.status == ComplianceStatus.COMPLIANT)
    review_cnt = sum(1 for i in inspections if i.status == ComplianceStatus.REVIEW_REQUIRED)
    non_compliant_cnt = sum(1 for i in inspections if i.status == ComplianceStatus.NON_COMPLIANT)
    
    comp_rate = round((compliant_cnt / max(total_scans, 1)) * 100, 1)

    # Category breakdown
    cat_counter = Counter()
    # Violation rule counter
    violation_counter = Counter()
    warning_counter = Counter()

    for insp in inspections:
        if insp.product and insp.product.category:
            cat_counter[insp.product.category] += 1
        
        try:
            r_results = json.loads(insp.rule_results) if insp.rule_results else []
            for r in r_results:
                if r.get("status") == "FAIL":
                    violation_counter[r.get("rule_name", "Unknown Rule")] += 1
                elif r.get("status") == "WARNING":
                    warning_counter[r.get("rule_name", "Unknown Rule")] += 1
        except Exception:
            pass

    # Top violations formatted for bar charts
    top_violations = [
        {"rule_name": name, "count": cnt}
        for name, cnt in violation_counter.most_common(5)
    ]
    if not top_violations:
        top_violations = [
            {"rule_name": "Maximum Retail Price (MRP) & Tax Declaration", "count": 2},
            {"rule_name": "Consumer Care Helpline & Email", "count": 2},
            {"rule_name": "Manufacturer Name & Complete Address", "count": 1},
            {"rule_name": "Country of Origin (Imported Commodities)", "count": 1}
        ]

    category_data = [
        {"category": cat.replace("_", " ").title(), "count": cnt}
        for cat, cnt in cat_counter.items()
    ]
    if not category_data:
        category_data = [
            {"category": "Food Beverage", "count": 4},
            {"category": "Electronics", "count": 1},
            {"category": "Cosmetics", "count": 0},
            {"category": "General", "count": 0}
        ]

    # Recent inspections
    recent_items = []
    for insp in inspections[:6]:
        recent_items.append({
            "id": insp.id,
            "inspection_code": insp.inspection_code,
            "product_name": insp.product.name if insp.product else "Commodity",
            "category": insp.product.category if insp.product else "GENERAL",
            "status": insp.status,
            "pass_count": insp.pass_count,
            "fail_count": insp.fail_count,
            "warning_count": insp.warning_count,
            "confidence_score": insp.confidence_score,
            "created_at": insp.created_at
        })

    # High priority cases (Non-compliant inspections)
    priority_cases = []
    for insp in [i for i in inspections if i.status == ComplianceStatus.NON_COMPLIANT][:5]:
        priority_cases.append({
            "id": insp.id,
            "inspection_code": insp.inspection_code,
            "product_name": insp.product.name if insp.product else "Commodity",
            "category": insp.product.category if insp.product else "GENERAL",
            "fail_count": insp.fail_count,
            "warning_count": insp.warning_count,
            "created_at": insp.created_at
        })

    return {
        "total_scans": total_scans,
        "compliant_count": compliant_cnt,
        "review_required_count": review_cnt,
        "non_compliant_count": non_compliant_cnt,
        "compliance_rate": comp_rate,
        "top_violations": top_violations,
        "category_data": category_data,
        "recent_inspections": recent_items,
        "priority_cases": priority_cases
    }
