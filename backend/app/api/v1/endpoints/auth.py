"""
Authentication endpoints for Firebase integration.
"""
import logging
from fastapi import APIRouter, HTTPException, Depends, Depends
from fastapi.security import OAuth2PasswordRequestForm
from app.models.dto import AuthRequest, AuthResponse, User
from app.models.user_schemas import UserCreate
from app.auth.firebase import verify_firebase_token
from app.services.firestore_service import firestore_service
from app.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/verify", response_model=AuthResponse)
async def verify_token(request: AuthRequest):
    """
    Verify Firebase ID token and return user information.
    """
    try:
        # Verify the Firebase token
        user_info = await verify_firebase_token(request.id_token)
        
        if settings.use_mocks:
            user = User(
                id="mock_user_123",
                email="mock@example.com",
                display_name="Mock User",
                created_at="2025-09-01T00:00:00Z",
                last_active="2025-09-03T10:30:00Z"
            )
        else:
            # Get or create user in Firestore
            user = await firestore_service.get_or_create_user(user_info)
        
        return AuthResponse(
            access_token=request.id_token,  # In a real app, you might generate your own JWT
            user=user,
            expires_in=3600
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token verification failed: {e}")
        raise HTTPException(status_code=401, detail="Authentication failed")


@router.post("/logout")
async def logout():
    """
    Logout endpoint (client should handle token removal).
    """
    return {"message": "Logged out successfully"}


@router.post("/login")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Login with email and password.
    In a real application, you would verify the password against a hashed version.
    """
    # This is a mock implementation.
    # You should replace this with actual user lookup and password verification.
    user = await firestore_service.get_user_by_email(form_data.username)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    # In a real app: if not pwd_context.verify(form_data.password, user.hashed_password):
    # For this mock, we'll just check if the password is not empty
    if not form_data.password:
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    # In a real app, you'd create a JWT here.
    # For now, we'll return a dummy token and user info.
    return {"token": "fake-jwt-token", "user": user}


@router.post("/register", response_model=User)
async def register_user(user_in: UserCreate):
    """
    Register a new user.
    """
    existing_user = await firestore_service.get_user_by_email(user_in.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # In a real app, you would hash the password here.
    # user_in.password = pwd_context.hash(user_in.password)
    
    new_user = await firestore_service.create_user(user_in)
    return new_user
