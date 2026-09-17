import os
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.config import settings, UPLOAD_DIR, DEMO_ASSETS_DIR, PROJECT_ROOT
from app.api import api_router
from app.seed import seed_database

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Prime database and seed data on startup
    try:
        seed_database()
    except Exception as e:
        print(f"Warning during startup seeding: {e}")
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description="Statutory Compliance Inspection System for Packaged Commodities under Legal Metrology Act, 2009 and Legal Metrology (Packaged Commodities) Rules, 2011 — Ministry of Consumer Affairs, Food & Public Distribution.",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static uploads and demo asset directories
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")
app.mount("/demo_assets", StaticFiles(directory=str(DEMO_ASSETS_DIR)), name="demo_assets")

# Include all API endpoints
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/api/status")
def root_status():
    return {
        "system": "VeriPack",
        "department": "Department of Consumer Affairs (DoCA)",
        "ministry": "Ministry of Consumer Affairs, Food & Public Distribution",
        "status": "OPERATIONAL",
        "statutory_framework": "Legal Metrology (Packaged Commodities) Rules, 2011",
        "api_docs": "/docs",
        "version": settings.PROJECT_VERSION
    }

FRONTEND_DIST = PROJECT_ROOT / "frontend" / "dist"
if FRONTEND_DIST.exists():
    assets_dir = FRONTEND_DIST / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="frontend_assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        # Allow API, docs, static uploads to pass through
        if (
            full_path.startswith("api")
            or full_path.startswith("uploads")
            or full_path.startswith("demo_assets")
            or full_path.startswith("docs")
            or full_path.startswith("openapi.json")
        ):
            raise HTTPException(status_code=404, detail="Not found")

        target = FRONTEND_DIST / full_path
        if full_path and target.is_file():
            return FileResponse(target)
        return FileResponse(FRONTEND_DIST / "index.html")
else:
    @app.get("/")
    def root_default():
        return root_status()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
