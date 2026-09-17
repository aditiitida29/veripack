from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ComplianceRuleBase(BaseModel):
    rule_code: str
    name: str
    description: str
    legal_reference: str
    required_field: str
    category_applicability: str = "ALL"
    severity: str = "FAIL"
    is_active: bool = True
    validation_type: str = "CUSTOM_LOGIC"
    pattern: Optional[str] = None

class ComplianceRuleCreate(ComplianceRuleBase):
    pass

class ComplianceRuleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    legal_reference: Optional[str] = None
    category_applicability: Optional[str] = None
    severity: Optional[str] = None
    is_active: Optional[bool] = None
    pattern: Optional[str] = None

class ComplianceRuleOut(ComplianceRuleBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
