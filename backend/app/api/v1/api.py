"""
Main API router that includes all endpoint routers.
"""
from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    auth_roadmap,
    content,
    reports,
    users,
    gamification,
    learning,
    admin,
    upload,
    checks,
    dashboard,
    documentation,
    community,
    media,
    firebase_auth,
    guest,
    misinformation,
    enhanced_learning,
    enhanced_community
)

api_router = APIRouter()

# Include all endpoint routers - prioritizing roadmap-compliant auth
api_router.include_router(guest.router, prefix="/guest", tags=["guest-access"])
api_router.include_router(auth_roadmap.router, prefix="/auth", tags=["authentication-roadmap"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(documentation.router, prefix="/docs-api", tags=["documentation"])
api_router.include_router(auth.router, prefix="/auth-legacy", tags=["authentication-legacy"])
api_router.include_router(firebase_auth.router, prefix="/auth-firebase", tags=["firebase-auth"])
api_router.include_router(content.router, prefix="/content", tags=["content-analysis"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(gamification.router, prefix="/gamification", tags=["gamification"])
api_router.include_router(learning.router, prefix="/learning", tags=["learning"])
api_router.include_router(enhanced_learning.router, prefix="/enhanced-learning", tags=["enhanced-learning-modules"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(upload.router, prefix="/upload", tags=["file-upload"])
api_router.include_router(media.router, prefix="/media", tags=["media-storage"])
api_router.include_router(checks.router, prefix="/checks", tags=["checks"])
api_router.include_router(community.router, prefix="/community", tags=["community"])
api_router.include_router(enhanced_community.router, prefix="/enhanced-community", tags=["enhanced-community-features"])
api_router.include_router(misinformation.router, prefix="/misinformation", tags=["enhanced-misinformation-detection"])
