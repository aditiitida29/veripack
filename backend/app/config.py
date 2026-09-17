import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BASE_DIR.parent
UPLOAD_DIR = PROJECT_ROOT / "uploads"
DEMO_ASSETS_DIR = PROJECT_ROOT / "demo_assets"

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
DEMO_ASSETS_DIR.mkdir(parents=True, exist_ok=True)

class Settings:
    PROJECT_NAME: str = "VeriPack - Legal Metrology Compliance Inspector"
    PROJECT_VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "doca-veripack-super-secret-key-2026-sih-compliance")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        f"sqlite:///{BASE_DIR}/veripack.db"
    )
    
    # CORS
    CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "*"
    ]
    
    # Tesseract configuration
    TESSERACT_CMD: str = os.getenv("TESSERACT_CMD", r"C:\Program Files\Tesseract-OCR\tesseract.exe")

settings = Settings()
