"""
User management endpoints.
"""
import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends
from app.models.dto import User, BaseResponse
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
                display_name=current_user.get("name"),
                created_at="2025-09-01T00:00:00Z",
                last_active="2025-09-03T10:30:00Z"
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


@router.put("/me")
async def update_user_profile(
    display_name: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Update current user profile."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    try:
        if settings.use_mocks:
            return BaseResponse(
                success=True,
                message="Mock: Profile updated"
            )
        
        updates = {}
        if display_name:
            updates["displayName"] = display_name
        
        if updates:
            await firestore_service.update_user_profile(current_user["uid"], updates)
        
        return BaseResponse(
            success=True,
            message="Profile updated successfully"
        )
        
    except Exception as e:
        logger.error(f"Error updating profile: {e}")
        raise HTTPException(status_code=500, detail="Failed to update profile")


@router.get("/{user_id}", response_model=User)
async def get_user_by_id(user_id: str):
    """Get user by ID (public info only)."""
    try:
        if settings.use_mocks:
            return User(
                id=user_id,
                email="hidden@example.com",
                display_name="Mock User",
                created_at="2025-09-01T00:00:00Z",
                last_active="2025-09-03T10:30:00Z"
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
