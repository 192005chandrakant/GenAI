"""
Main API router that includes all endpoint routers.
"""
from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    content,
    reports,
    users,
    gamification,
    learning,
    admin,
    upload,
    checks,
    dashboard,
    documentation
)

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(documentation.router, prefix="/docs-api", tags=["documentation"])
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(content.router, prefix="/content", tags=["content-analysis"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(gamification.router, prefix="/gamification", tags=["gamification"])
api_router.include_router(learning.router, prefix="/learning", tags=["learning"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(upload.router, prefix="/upload", tags=["file-upload"])
api_router.include_router(checks.router, prefix="/checks", tags=["checks"])
