"""
Firebase authentication endpoints.
"""
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from typing import Optional, Dict, Any
import logging

from app.auth.firebase import verify_firebase_token, get_current_user
from app.models.user_schemas import UserResponse

logger = logging.getLogger(__name__)

router = APIRouter()


class FirebaseLoginRequest(BaseModel):
    idToken: str
    user: Dict[str, Any]


class FirebaseLoginResponse(BaseModel):
    success: bool
    message: str
    user: Optional[Dict[str, Any]] = None
    token: Optional[str] = None


@router.post("/firebase-login", response_model=FirebaseLoginResponse)
async def firebase_login(request: FirebaseLoginRequest):
    """
    Handle Firebase authentication login/signup.
    
    This endpoint receives a Firebase ID token, verifies it,
    and creates or updates the user in our system.
    """
    try:
        # Verify the Firebase ID token
        firebase_user = await verify_firebase_token(request.idToken)
        
        # Create or update user in our system
        user_data = {
            "uid": firebase_user["uid"],
            "email": firebase_user["email"],
            "full_name": firebase_user.get("name") or request.user.get("displayName"),
            "photo_url": firebase_user.get("picture") or request.user.get("photoURL"),
            "email_verified": firebase_user.get("email_verified", False),
            "is_admin": firebase_user.get("admin", False),
            "provider": "firebase",
            "points": 0,
            "level": 1,
            "preferences": {
                "language": "en",
                "notifications": True,
                "privacy_level": "public"
            }
        }
        
        logger.info(f"Firebase user authenticated: {firebase_user['uid']}")
        
        return FirebaseLoginResponse(
            success=True,
            message="Authentication successful",
            user=user_data,
            token=request.idToken  # Return the same token for client use
        )
        
    except HTTPException as e:
        logger.error(f"Firebase authentication failed: {e.detail}")
        raise e
        
    except Exception as e:
        logger.error(f"Unexpected error in Firebase authentication: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication service error"
        )


@router.get("/profile", response_model=UserResponse)
async def get_user_profile(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Get current user profile information.
    
    This endpoint returns the current user's profile data.
    """
    try:
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated"
            )
        
        # Transform Firebase user data to our user response format
        user_response = {
            "id": current_user["uid"],
            "email": current_user["email"],
            "full_name": current_user.get("name", ""),
            "photo_url": current_user.get("picture"),
            "is_admin": current_user.get("admin", False),
            "email_verified": current_user.get("email_verified", False),
            "points": current_user.get("points", 0),
            "level": current_user.get("level", 1),
            "preferences": current_user.get("preferences", {
                "language": "en",
                "notifications": True,
                "privacy_level": "public"
            }),
            "created_at": None,  # Firebase doesn't provide creation time in token
            "last_active_at": None
        }
        
        return UserResponse(**user_response)
        
    except HTTPException:
        raise
        
    except Exception as e:
        logger.error(f"Error fetching user profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch user profile"
        )


@router.post("/refresh-token")
async def refresh_token(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Refresh authentication token.
    
    For Firebase, we don't need to refresh tokens server-side.
    The client handles token refresh automatically.
    """
    try:
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated"
            )
        
        return {
            "success": True,
            "message": "Token is valid",
            "user": current_user
        }
        
    except HTTPException:
        raise
        
    except Exception as e:
        logger.error(f"Error refreshing token: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed"
        )
