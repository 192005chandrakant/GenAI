"""
User management endpoints.
"""
import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from app.models.dto import User, BaseResponse
from app.models.user_schemas import UserCreate, UserUpdate, UserPreferences
from app.auth.firebase import get_current_user
from app.services.firestore_service import firestore_service
from app.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/me", response_model=User)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current user information."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    try:
        if settings.use_mocks:
            return User(
                id=current_user["uid"],
                email=current_user["email"],
                full_name=current_user.get("name", "Mock User"),
                photoUrl="https://via.placeholder.com/150",
                points=1250,
                level=5,
                isAdmin=current_user["email"] == "admin@example.com",
                preferences={
                    "language": "en",
                    "notifications": True,
                    "privacyLevel": "public"
                },
                createdAt="2025-09-01T00:00:00Z",
                lastActiveAt="2025-09-09T10:30:00Z"
            )
        
        user = await firestore_service.get_user_by_id(current_user["uid"])
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user info: {e}")
        raise HTTPException(status_code=500, detail="Failed to get user information")


@router.put("/me", response_model=User)
async def update_user_profile(
    user_update: UserUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update current user profile."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    try:
        if settings.use_mocks:
            return User(
                id=current_user["uid"],
                email=current_user["email"],
                full_name=user_update.full_name or "Updated User",
                photoUrl=user_update.photoUrl or "https://via.placeholder.com/150",
                points=1250,
                level=5,
                isAdmin=False,
                preferences={
                    "language": "en",
                    "notifications": True,
                    "privacyLevel": "public"
                },
                createdAt="2025-09-01T00:00:00Z",
                lastActiveAt="2025-09-09T10:30:00Z"
            )
        
        updated_user = await firestore_service.update_user_profile(
            current_user["uid"], 
            user_update.dict(exclude_unset=True)
        )
        
        return updated_user
        
    except Exception as e:
        logger.error(f"Error updating profile: {e}")
        raise HTTPException(status_code=500, detail="Failed to update profile")


@router.patch("/me/preferences", response_model=BaseResponse)
async def update_user_preferences(
    preferences: UserPreferences,
    current_user: dict = Depends(get_current_user)
):
    """Update user preferences."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    try:
        if settings.use_mocks:
            return BaseResponse(
                success=True,
                message="Preferences updated successfully"
            )
        
        await firestore_service.update_user_preferences(
            current_user["uid"], 
            preferences.dict(exclude_unset=True)
        )
        
        return BaseResponse(
            success=True,
            message="Preferences updated successfully"
        )
        
    except Exception as e:
        logger.error(f"Error updating preferences: {e}")
        raise HTTPException(status_code=500, detail="Failed to update preferences")


@router.get("/me/history")
async def get_user_history(
    limit: int = Query(20, le=100),
    offset: int = Query(0, ge=0),
    content_type: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user)
):
    """Get user's content analysis history."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    try:
        if settings.use_mocks:
            return {
                "history": [
                    {
                        "id": "check_001",
                        "content": "Sample analyzed content...",
                        "verdict": "Mostly True",
                        "score": 75,
                        "timestamp": "2025-09-04T10:30:00Z",
                        "content_type": "text"
                    },
                    {
                        "id": "check_002", 
                        "content": "Another piece of content...",
                        "verdict": "False",
                        "score": 25,
                        "timestamp": "2025-09-03T14:20:00Z",
                        "content_type": "url"
                    }
                ],
                "total": 2,
                "has_more": False
            }
        
        history = await firestore_service.get_user_analysis_history(
            user_id=current_user["uid"],
            limit=limit,
            offset=offset,
            content_type=content_type
        )
        
        return history
        
    except Exception as e:
        logger.error(f"Error getting user history: {e}")
        raise HTTPException(status_code=500, detail="Failed to get user history")


@router.get("/me/stats")
async def get_user_stats(current_user: dict = Depends(get_current_user)):
    """Get user statistics and analytics."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    try:
        if settings.use_mocks:
            return {
                "total_checks": 87,
                "accuracy_rate": 88.5,
                "total_points": 1250,
                "level": 5,
                "checks_this_week": 12,
                "checks_this_month": 47,
                "favorite_categories": ["politics", "health", "technology"],
                "streak_days": 8,
                "achievements_count": 15,
                "rank_percentile": 25
            }
        
        stats = await firestore_service.get_user_statistics(current_user["uid"])
        return stats
        
    except Exception as e:
        logger.error(f"Error getting user stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get user statistics")


@router.get("/{user_id}", response_model=User)
async def get_user_by_id(user_id: str):
    """Get user by ID (public info only)."""
    try:
        if settings.use_mocks:
            return User(
                id=user_id,
                email="hidden@example.com",
                full_name="Public User",
                photoUrl="https://via.placeholder.com/150",
                points=750,
                level=3,
                isAdmin=False,
                preferences={
                    "language": "en",
                    "notifications": True,
                    "privacyLevel": "public"
                },
                createdAt="2025-09-01T00:00:00Z",
                lastActiveAt="2025-09-08T15:45:00Z"
            )
        
        user = await firestore_service.get_user_public_info(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get user")


@router.delete("/me", response_model=BaseResponse)
async def delete_user_account(current_user: dict = Depends(get_current_user)):
    """Delete current user account."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    try:
        if settings.use_mocks:
            return BaseResponse(
                success=True,
                message="Account deletion initiated"
            )
        
        await firestore_service.delete_user_account(current_user["uid"])
        
        return BaseResponse(
            success=True,
            message="Account deleted successfully"
        )
        
    except Exception as e:
        logger.error(f"Error deleting account: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete account")


@router.get("/search")
async def search_users(
    query: str = Query(..., min_length=3),
    limit: int = Query(10, le=50),
    offset: int = Query(0, ge=0)
):
    """Search for users by name or username."""
    try:
        if settings.use_mocks:
            return {
                "users": [
                    {
                        "id": "user_001",
                        "name": "John Doe",
                        "level": 5,
                        "points": 1200,
                        "avatar": "https://via.placeholder.com/150"
                    },
                    {
                        "id": "user_002",
                        "name": "Jane Smith", 
                        "level": 3,
                        "points": 850,
                        "avatar": "https://via.placeholder.com/150"
                    }
                ],
                "total": 2,
                "has_more": False
            }
        
        results = await firestore_service.search_users(
            query=query,
            limit=limit,
            offset=offset
        )
        
        return results
        
    except Exception as e:
        logger.error(f"Error searching users: {e}")
        raise HTTPException(status_code=500, detail="Failed to search users")
