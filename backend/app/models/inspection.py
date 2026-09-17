import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class ComplianceStatus:
    COMPLIANT = "COMPLIANT"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    NON_COMPLIANT = "NON_COMPLIANT"

class Inspection(Base):
    __tablename__ = "inspections"

    id = Column(Integer, primary_key=True, index=True)
    inspection_code = Column(String(50), unique=True, index=True, nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    inspector_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(String(50), default=ComplianceStatus.REVIEW_REQUIRED, nullable=False)
    
    # Quantitative summary
    pass_count = Column(Integer, default=0)
    fail_count = Column(Integer, default=0)
    warning_count = Column(Integer, default=0)
    confidence_score = Column(Integer, default=0)  # 0 to 100 percentage
    
    # Detailed payloads in JSON format
    extracted_fields = Column(Text, nullable=False)  # JSON string
    rule_results = Column(Text, nullable=False)      # JSON string
    bounding_boxes = Column(Text, nullable=True)     # JSON string
    raw_ocr_text = Column(Text, nullable=True)
    image_paths = Column(Text, nullable=False)       # JSON string list
    
    inspector_remarks = Column(Text, nullable=True)
    is_demo = Column(Boolean, default=False)
    pdf_path = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    product = relationship("Product", back_populates="inspections")
    inspector = relationship("User")
