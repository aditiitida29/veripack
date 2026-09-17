import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.orm import relationship
from app.database import Base

class ProductCategory:
    FOOD_BEVERAGE = "FOOD_BEVERAGE"
    COSMETICS = "COSMETICS"
    ELECTRONICS = "ELECTRONICS"
    PHARMACEUTICALS_CHEMICALS = "PHARMACEUTICALS_CHEMICALS"
    HOUSEHOLD = "HOUSEHOLD"
    GENERAL = "GENERAL"

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    brand = Column(String(255), nullable=True)
    category = Column(String(100), default=ProductCategory.GENERAL, nullable=False)
    barcode = Column(String(100), nullable=True, index=True)
    is_imported = Column(Boolean, default=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    inspections = relationship("Inspection", back_populates="product", cascade="all, delete-orphan")
