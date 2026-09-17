import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from app.database import Base

class RuleSeverity:
    FAIL = "FAIL"
    WARNING = "WARNING"

class ComplianceRule(Base):
    __tablename__ = "compliance_rules"

    id = Column(Integer, primary_key=True, index=True)
    rule_code = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    legal_reference = Column(String(255), nullable=False)
    required_field = Column(String(100), nullable=False, index=True)
    category_applicability = Column(String(255), default="ALL", nullable=False)
    severity = Column(String(20), default=RuleSeverity.FAIL, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    validation_type = Column(String(50), default="CUSTOM_LOGIC", nullable=False)
    pattern = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
