from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ProductBase(BaseModel):
    name: str
    brand: Optional[str] = None
    category: str = "GENERAL"
    barcode: Optional[str] = None
    is_imported: bool = False
    description: Optional[str] = None

class ProductCreate(ProductBase):
    pass

class ProductOut(ProductBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
