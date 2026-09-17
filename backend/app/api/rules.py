from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.rule import ComplianceRule, RuleSeverity
from app.models.user import User, UserRole
from app.schemas.rule import ComplianceRuleOut, ComplianceRuleCreate, ComplianceRuleUpdate
from app.api.deps import get_current_user, require_role

router = APIRouter(prefix="/rules", tags=["Compliance Rules Management"])

@router.get("", response_model=List[ComplianceRuleOut])
def list_rules(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(ComplianceRule).order_by(ComplianceRule.id.asc()).all()

@router.post("", response_model=ComplianceRuleOut)
def create_rule(
    rule_in: ComplianceRuleCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_role([UserRole.SUPER_ADMIN]))
):
    existing = db.query(ComplianceRule).filter(ComplianceRule.rule_code == rule_in.rule_code).first()
    if existing:
        raise HTTPException(status_code=400, detail="Rule with this rule_code already exists")
    
    new_rule = ComplianceRule(**rule_in.dict())
    db.add(new_rule)
    db.commit()
    db.refresh(new_rule)
    return new_rule

@router.put("/{id}", response_model=ComplianceRuleOut)
def update_rule(
    id: int,
    rule_update: ComplianceRuleUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_role([UserRole.SUPER_ADMIN]))
):
    rule = db.query(ComplianceRule).filter(ComplianceRule.id == id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Compliance rule not found")
    
    for key, val in rule_update.dict(exclude_unset=True).items():
        setattr(rule, key, val)
        
    db.commit()
    db.refresh(rule)
    return rule

@router.patch("/{id}/toggle", response_model=ComplianceRuleOut)
def toggle_rule(
    id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_role([UserRole.SUPER_ADMIN]))
):
    rule = db.query(ComplianceRule).filter(ComplianceRule.id == id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Compliance rule not found")
    
    rule.is_active = not rule.is_active
    db.commit()
    db.refresh(rule)
    return rule
