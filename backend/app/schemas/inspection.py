from pydantic import BaseModel
from typing import Optional, Any, List, Dict
from datetime import datetime

class RuleEvaluationResult(BaseModel):
    rule_code: str
    rule_name: str
    field: str
    status: str  # PASS, FAIL, WARNING, NOT_APPLICABLE
    message: str
    evidence: Optional[str] = None
    confidence: float = 0.0
    legal_reference: str
    severity: str = "FAIL"
    bounding_box: Optional[Dict[str, Any]] = None

class ExtractedFieldDetail(BaseModel):
    field_name: str
    value: Optional[str] = None
    status: str  # DETECTED, MISSING, AMBIGUOUS
    confidence: float = 0.0
    evidence: Optional[str] = None
    bounding_box: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None

class InspectionCreate(BaseModel):
    product_name: str
    category: str = "GENERAL"
    brand: Optional[str] = None
    barcode: Optional[str] = None
    is_imported: bool = False
    inspector_remarks: Optional[str] = None

class InspectionUpdateRemarks(BaseModel):
    inspector_remarks: str

class InspectionOut(BaseModel):
    id: int
    inspection_code: str
    product_id: int
    inspector_id: int
    status: str
    pass_count: int
    fail_count: int
    warning_count: int
    confidence_score: int
    extracted_fields: Dict[str, Any]
    rule_results: List[Dict[str, Any]]
    bounding_boxes: Optional[List[Dict[str, Any]]] = None
    raw_ocr_text: Optional[str] = None
    image_paths: List[str]
    inspector_remarks: Optional[str] = None
    is_demo: bool = False
    pdf_path: Optional[str] = None
    created_at: datetime
    product: Optional[Any] = None
    inspector_name: Optional[str] = None

    class Config:
        from_attributes = True

class InspectionListItem(BaseModel):
    id: int
    inspection_code: str
    product_id: int
    product_name: str
    category: str
    inspector_id: int
    inspector_name: str
    status: str
    pass_count: int
    fail_count: int
    warning_count: int
    confidence_score: int
    image_paths: List[str]
    created_at: datetime
    is_demo: bool = False
