from fastapi import APIRouter
from app.api.auth import router as auth_router
from app.api.scans import router as scans_router
from app.api.products import router as products_router
from app.api.rules import router as rules_router
from app.api.dashboard import router as dashboard_router
from app.api.reports import router as reports_router
from app.api.users import router as users_router

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(scans_router)
api_router.include_router(products_router)
api_router.include_router(rules_router)
api_router.include_router(dashboard_router)
api_router.include_router(reports_router)
api_router.include_router(users_router)
