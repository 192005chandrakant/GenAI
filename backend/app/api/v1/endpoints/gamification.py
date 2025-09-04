"""
Placeholder endpoints for gamification features.
"""
import logging
from fastapi import APIRouter
from app.models.dto import BaseResponse
from app.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/leaderboard")
async def get_leaderboard():
    """Get user leaderboard."""
    if settings.use_mocks:
        return {"leaderboard": [], "message": "Feature coming soon"}
    return {"leaderboard": [], "message": "Feature coming soon"}


@router.get("/achievements")
async def get_achievements():
    """Get available achievements."""
    if settings.use_mocks:
        return {"achievements": [], "message": "Feature coming soon"}
    return {"achievements": [], "message": "Feature coming soon"}
