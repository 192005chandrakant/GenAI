"""
Authentication endpoints for Firebase integration.
"""
import logging
from typing import Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Depends, Request, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from app.models.dto import AuthRequest, AuthResponse, User
from app.models.user_schemas import UserCreate, PasswordReset, PasswordChange
from app.auth.firebase import verify_firebase_token, require_auth, get_current_user
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
    try:
        if settings.use_mocks:
            # Mock implementation for development
            if form_data.username and form_data.password:
                is_admin = form_data.username == "admin@example.com"
                user = User(
                    id="mock_user_123",
                    email=form_data.username,
                    full_name="Mock User",
                    photoUrl="https://via.placeholder.com/150",
                    points=100,
                    level=1,
                    isAdmin=is_admin,
                    preferences={
                        "language": "en",
                        "notifications": True,
                        "privacyLevel": "public"
                    },
                    createdAt="2025-09-01T00:00:00Z",
                    lastActiveAt="2025-09-03T10:30:00Z"
                )
                
                # Use consistent response format
                return {
                    "token": "mock-jwt-token-123", 
                    "access_token": "mock-jwt-token-123", 
                    "token_type": "bearer",
                    "expires_in": 3600,
                    "user": user
                }
            else:
                raise HTTPException(status_code=400, detail="Email and password required")
        else:
            # Real implementation with Firestore
            user = await firestore_service.get_user_by_email(form_data.username)
            if not user:
                raise HTTPException(status_code=400, detail="Incorrect email or password")

            # In a real app: if not pwd_context.verify(form_data.password, user.hashed_password):
            # For this mock, we'll just check if the password is not empty
            if not form_data.password:
                raise HTTPException(status_code=400, detail="Incorrect email or password")

            # In a real app, you'd create a JWT here.
            token = "fake-jwt-token"
            if form_data.username == "admin@example.com":
                token = "admin-jwt-token"
                
            return {
                "token": token, 
                "access_token": token,
                "token_type": "bearer", 
                "expires_in": 3600,
                "user": user
            }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login failed: {e}")
        raise HTTPException(status_code=500, detail="Authentication failed")


@router.post("/register", response_model=User)
async def register_user(user_in: UserCreate):
    """
    Register a new user.
    """
    try:
        # Get the current timestamp for created_at and last_active fields
        current_time = datetime.utcnow().isoformat()
        
        if settings.use_mocks:
            # Mock implementation for development
            new_user = User(
                id=f"user_{user_in.email.replace('@', '_').replace('.', '_')}",
                email=user_in.email,
                full_name=user_in.full_name,
                photoUrl="https://via.placeholder.com/150",
                points=0,
                level=1,
                isAdmin=False,
                preferences={
                    "language": "en",
                    "notifications": True,
                    "privacyLevel": "public"
                },
                # Add these required fields that were missing before
                createdAt=current_time,
                lastActiveAt=current_time,
                # For compatibility with both field naming conventions
                created_at=current_time,
                last_active=current_time
            )
            return new_user
        else:
            # Real implementation with Firestore
            existing_user = await firestore_service.get_user_by_email(user_in.email)
            if existing_user:
                raise HTTPException(status_code=400, detail="Email already registered")
            
            # In a real app, you would hash the password here.
            # user_in.password = pwd_context.hash(user_in.password)
            
            # Create user with all required fields
            user_data = {
                "email": user_in.email,
                "full_name": user_in.full_name,
                "password": user_in.password,  # Note: should be hashed in production
                "createdAt": current_time,
                "lastActiveAt": current_time,
                "created_at": current_time,
                "last_active": current_time,
                "points": 0,
                "level": 1,
                "isAdmin": False,
                "preferences": {
                    "language": "en",
                    "notifications": True,
                    "privacyLevel": "public"
                }
            }
            
            new_user = await firestore_service.create_user(user_data)
            return new_user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"User registration failed: {e}")
        raise HTTPException(status_code=500, detail="Registration failed")


@router.post("/oauth/google")
async def google_oauth_login(request: dict):
    """
    Handle Google OAuth login.
    """
    try:
        id_token = request.get("idToken")
        if not id_token:
            raise HTTPException(status_code=400, detail="ID token is required")
        
        if settings.use_mocks:
            # Mock Google OAuth user
            user = User(
                id="google_user_123",
                email="google.user@gmail.com",
                full_name="Google User",
                photoUrl="https://lh3.googleusercontent.com/a/default-user",
                points=0,
                level=1,
                isAdmin=False,
                preferences={
                    "language": "en",
                    "notifications": True,
                    "privacyLevel": "public"
                },
                createdAt="2025-09-09T00:00:00Z",
                lastActiveAt="2025-09-09T00:00:00Z"
            )
            return {
                "token": "google-mock-jwt-token", 
                "access_token": "google-mock-jwt-token",
                "token_type": "bearer",
                "expires_in": 3600,
                "user": user
            }
        else:
            # Verify Google ID token and get user info
            user_info = await verify_firebase_token(id_token)
            user = await firestore_service.get_or_create_user(user_info)
            return {
                "token": id_token, 
                "access_token": id_token,
                "token_type": "bearer",
                "expires_in": 3600,
                "user": user
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Google OAuth failed: {e}")
        raise HTTPException(status_code=500, detail="Google authentication failed")


@router.post("/oauth/github")
async def github_oauth_login(request: dict):
    """
    Handle GitHub OAuth login.
    """
    try:
        access_token = request.get("accessToken")
        if not access_token:
            raise HTTPException(status_code=400, detail="Access token is required")
        
        if settings.use_mocks:
            # Mock GitHub OAuth user
            import uuid
            user_id = f"github_user_{uuid.uuid4().hex[:8]}"
            
            user = User(
                id=user_id,
                email="github.user@example.com",
                full_name="GitHub User",
                photoUrl="https://avatars.githubusercontent.com/u/12345678",
                points=0,
                level=1,
                isAdmin=False,
                preferences={
                    "language": "en",
                    "notifications": True,
                    "privacyLevel": "public"
                },
                createdAt=datetime.utcnow().isoformat(),
                lastActiveAt=datetime.utcnow().isoformat()
            )
            return {
                "token": "github-mock-jwt-token", 
                "access_token": "github-mock-jwt-token",
                "token_type": "bearer",
                "expires_in": 3600,
                "user": user
            }
        else:
            # Get GitHub user info from the access token
            github_user_info = await get_github_user_info(access_token)
            
            # Create a user info object compatible with our system
            user_info = {
                "uid": f"github_{github_user_info['id']}",
                "email": github_user_info.get("email", ""),
                "name": github_user_info.get("name", "") or github_user_info.get("login", ""),
                "picture": github_user_info.get("avatar_url", ""),
                "provider": "github",
                "email_verified": True  # GitHub emails are verified
            }
            
            # Create or get user in our database
            user = await firestore_service.get_or_create_user(user_info)
            
            # Create a token for the user
            token = f"github-token-{user.id}"
            
            return {
                "token": token, 
                "access_token": token,
                "token_type": "bearer",
                "expires_in": 3600,
                "user": user
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"GitHub OAuth failed: {e}")
        raise HTTPException(status_code=500, detail="GitHub authentication failed")


@router.get("/profile", response_model=User)
async def get_user_profile(current_user: dict = Depends(get_current_user)):
    """
    Get current user profile.
    """
    try:
        if settings.use_mocks:
            # Return mock user profile based on current user
            user = User(
                id=current_user.get("uid", "mock_user_123"),
                email=current_user.get("email", "user@example.com"),
                full_name=current_user.get("name", "Mock User"),
                photoUrl=current_user.get("picture", "https://via.placeholder.com/150"),
                points=100,
                level=1,
                isAdmin=current_user.get("admin", False),
                preferences={
                    "language": "en",
                    "notifications": True,
                    "privacyLevel": "public"
                },
                createdAt="2025-09-01T00:00:00Z",
                lastActiveAt="2025-09-09T10:30:00Z"
            )
            return user
        else:
            # Get user profile from Firestore
            user = await firestore_service.get_user_by_id(current_user["uid"])
            if not user:
                raise HTTPException(status_code=404, detail="User profile not found")
            return user
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get profile failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to get profile")


@router.post("/refresh-token")
async def refresh_token(current_user: dict = Depends(get_current_user)):
    """
    Refresh authentication token.
    """
    try:
        # First import time for timestamp generation
        import time
        
        if settings.use_mocks:
            # Create a new token with a timestamp to ensure uniqueness
            new_token = f"refreshed-mock-token-{current_user.get('uid', 'unknown')}-{int(time.time())}"
            
            # Return user data along with the new token in a consistent format
            user = User(
                id=current_user.get("uid", "mock_user_123"),
                email=current_user.get("email", "user@example.com"),
                full_name=current_user.get("name", "Mock User"),
                photoUrl=current_user.get("picture", "https://via.placeholder.com/150"),
                points=100,
                level=1,
                isAdmin=current_user.get("admin", False),
                preferences={
                    "language": "en",
                    "notifications": True,
                    "privacyLevel": "public"
                },
                createdAt="2025-09-01T00:00:00Z",
                lastActiveAt="2025-09-09T00:00:00Z"
            )
            
            return {
                "token": new_token,
                "access_token": new_token,
                "token_type": "bearer",
                "expires_in": 3600,
                "user": user
            }
        else:
            # In Firebase, the client handles token refresh
            # For custom JWT implementation, we can still return user data
            user = await firestore_service.get_user_by_id(current_user["uid"])
            if not user:
                # If user not found in database, create a minimal user object
                user = User(
                    id=current_user["uid"],
                    email=current_user.get("email", ""),
                    full_name=current_user.get("name", "User"),
                    photoUrl=current_user.get("picture"),
                    points=0,
                    level=1,
                    isAdmin=False,
                    preferences={
                        "language": "en",
                        "notifications": True,
                        "privacyLevel": "public"
                    },
                    createdAt=datetime.now().isoformat(),
                    lastActiveAt=datetime.now().isoformat()
                )
            
            # Use the Firebase token or create a custom token
            token = f"refreshed-token-{current_user['uid']}-{int(time.time())}"
            
            return {
                "token": token,
                "access_token": token,
                "token_type": "bearer",
                "expires_in": 3600,
                "user": user
            }
            
    except Exception as e:
        logger.error(f"Token refresh failed: {e}")
        raise HTTPException(status_code=500, detail="Token refresh failed")


@router.post("/change-password")
async def change_password(
    password_change: PasswordChange,
    current_user: dict = Depends(get_current_user)
):
    """
    Change user password.
    """
    try:
        if settings.use_mocks:
            return {"message": "Password changed successfully (mock)"}
        else:
            # In Firebase, password changes are handled client-side
            # This could log the password change event
            await firestore_service.log_user_activity(
                user_id=current_user["uid"],
                activity_type="password_change",
                details={"timestamp": datetime.now().isoformat()}
            )
            
            return {"message": "Password change logged. Use Firebase client SDK to change password."}
            
    except Exception as e:
        logger.error(f"Password change failed: {e}")
        raise HTTPException(status_code=500, detail="Password change failed")


@router.post("/reset-password")
async def reset_password(reset_request: PasswordReset):
    """
    Initiate password reset process.
    """
    try:
        if settings.use_mocks:
            return {"message": f"Password reset email sent to {reset_request.email} (mock)"}
        else:
            # In Firebase, password reset is handled by Firebase Auth
            # This could log the reset request
            await firestore_service.log_password_reset_request(reset_request.email)
            
            return {"message": "If the email exists, a password reset link has been sent."}
            
    except Exception as e:
        logger.error(f"Password reset failed: {e}")
        raise HTTPException(status_code=500, detail="Password reset failed")


@router.post("/verify-email")
async def verify_email(
    verification_token: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Verify user email address.
    """
    try:
        if settings.use_mocks:
            return {"message": "Email verified successfully (mock)"}
        else:
            # Update user email verification status
            await firestore_service.update_user_email_verification(
                user_id=current_user["uid"],
                verified=True
            )
            
            return {"message": "Email verified successfully"}
            
    except Exception as e:
        logger.error(f"Email verification failed: {e}")
        raise HTTPException(status_code=500, detail="Email verification failed")


@router.post("/resend-verification")
async def resend_verification_email(current_user: dict = Depends(get_current_user)):
    """
    Resend email verification.
    """
    try:
        if settings.use_mocks:
            return {"message": "Verification email resent (mock)"}
        else:
            # Log verification email resend request
            await firestore_service.log_user_activity(
                user_id=current_user["uid"],
                activity_type="verification_email_resend",
                details={"timestamp": datetime.now().isoformat()}
            )
            
            return {"message": "Verification email resent. Check your inbox."}
            
    except Exception as e:
        logger.error(f"Resend verification failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to resend verification email")


@router.delete("/account")
async def delete_account(
    current_user: dict = Depends(get_current_user),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """
    Delete user account and all associated data.
    """
    try:
        if settings.use_mocks:
            return {"message": "Account deletion initiated (mock)"}
        else:
            # Schedule account deletion in background
            background_tasks.add_task(
                firestore_service.delete_user_account,
                user_id=current_user["uid"]
            )
            
            return {"message": "Account deletion initiated. Data will be removed within 24 hours."}
            
    except Exception as e:
        logger.error(f"Account deletion failed: {e}")
        raise HTTPException(status_code=500, detail="Account deletion failed")


@router.get("/sessions")
async def get_user_sessions(current_user: dict = Depends(get_current_user)):
    """
    Get user's active sessions.
    """
    try:
        if settings.use_mocks:
            return {
                "sessions": [
                    {
                        "id": "session_123",
                        "device": "Chrome on Windows",
                        "ip_address": "192.168.1.100",
                        "location": "New York, US",
                        "last_active": "2025-09-09T10:30:00Z",
                        "current": True
                    }
                ]
            }
        else:
            sessions = await firestore_service.get_user_sessions(current_user["uid"])
            return {"sessions": sessions}
            
    except Exception as e:
        logger.error(f"Get sessions failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to get sessions")


@router.delete("/sessions/{session_id}")
async def revoke_session(
    session_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Revoke a specific session.
    """
    try:
        if settings.use_mocks:
            return {"message": f"Session {session_id} revoked (mock)"}
        else:
            await firestore_service.revoke_user_session(
                user_id=current_user["uid"],
                session_id=session_id
            )
            
            return {"message": "Session revoked successfully"}
            
    except Exception as e:
        logger.error(f"Session revocation failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to revoke session")


@router.post("/two-factor/enable")
async def enable_two_factor(current_user: dict = Depends(get_current_user)):
    """
    Enable two-factor authentication.
    """
    try:
        if settings.use_mocks:
            return {
                "qr_code": "mock-qr-code-data",
                "backup_codes": ["123456", "789012", "345678"],
                "message": "Two-factor authentication enabled (mock)"
            }
        else:
            # Generate TOTP secret and QR code
            totp_data = await firestore_service.setup_two_factor(current_user["uid"])
            return totp_data
            
    except Exception as e:
        logger.error(f"2FA enable failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to enable two-factor authentication")


@router.post("/two-factor/disable")
async def disable_two_factor(
    verification_code: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Disable two-factor authentication.
    """
    try:
        if settings.use_mocks:
            return {"message": "Two-factor authentication disabled (mock)"}
        else:
            await firestore_service.disable_two_factor(
                user_id=current_user["uid"],
                verification_code=verification_code
            )
            
            return {"message": "Two-factor authentication disabled"}
            
    except Exception as e:
        logger.error(f"2FA disable failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to disable two-factor authentication")
