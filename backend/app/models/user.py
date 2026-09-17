import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from app.database import Base

class UserRole:
    SUPER_ADMIN = "SUPER_ADMIN"
    INSPECTOR = "INSPECTOR"
    VIEWER = "VIEWER"
    CONSUMER = "CONSUMER"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(String(50), default=UserRole.CONSUMER, nullable=False)
    department = Column(String(255), default="Department of Consumer Affairs (DoCA)")
    badge_number = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
