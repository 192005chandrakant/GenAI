"""
Authentication endpoints according to roadmap specifications.
Implements Firebase Auth, OAuth providers, guest access, and user management.
"""

from fastapi import APIRouter, HTTPException, Depends, Header, Request, status
from typing import Optional, Dict, Any, Union
import uuid
import logging
from datetime import datetime, timedelta
import jwt
from passlib.context import CryptContext

from app.models.auth_schemas import (
    FirebaseLoginRequest,
    GoogleOAuthRequest, 
    GitHubOAuthRequest,
    EmailPasswordRequest,
    RegisterRequest,
    OAuthResponse,
    UserProfile,
    UserProfileUpdate,
    TokenResponse,
    RefreshTokenRequest,
    PasswordResetRequest,
    PasswordResetConfirm,
    AdminUserRequest,
    GuestUpgradeRequest,
    UserPreferences
)
from app.auth.firebase import verify_firebase_token, get_current_user, get_github_user_info
from app.core.config import get_settings
# Removed import for get_db_connection as it doesn't exist and isn't used

logger = logging.getLogger(__name__)
settings = get_settings()
router = APIRouter()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# In-memory storage for demo (use database in production)
users_db: Dict[str, Dict[str, Any]] = {}
refresh_tokens: Dict[str, Dict[str, Any]] = {}

def create_access_token(user_data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token."""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=24)
    
    to_encode = {
        "user_id": user_data["id"],
        "email": user_data["email"],
        "role": user_data.get("role", "user"),
        "exp": expire
    }
    
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm="HS256")

def create_refresh_token(user_id: str) -> str:
    """Create refresh token."""
    token = f"refresh_{uuid.uuid4().hex}"
    refresh_tokens[token] = {
        "user_id": user_id,
        "created_at": datetime.utcnow(),
        "expires_at": datetime.utcnow() + timedelta(days=30)
    }
    return token

def hash_password(password: str) -> str:
    """Hash password using bcrypt."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash."""
    return pwd_context.verify(plain_password, hashed_password)

def create_user_profile(user_data: Dict[str, Any]) -> UserProfile:
    """Create user profile from user data."""
    now = datetime.utcnow()
    
    profile_data = {
        "id": user_data.get("id", f"user_{uuid.uuid4().hex[:8]}"),
        "email": user_data["email"],
        "full_name": user_data.get("full_name", user_data.get("name", "User")),
        "photo_url": user_data.get("photo_url", user_data.get("picture")),
        "is_admin": user_data.get("is_admin", False),
        "role": user_data.get("role", "user"),
        "provider": user_data.get("provider", "firebase"),
        "email_verified": user_data.get("email_verified", True),
        "points": user_data.get("points", 0),
        "level": user_data.get("level", 1),
        "badges": user_data.get("badges", []),
        "streak_days": user_data.get("streak_days", 0),
        "total_checks": user_data.get("total_checks", 0),
        "accuracy_score": user_data.get("accuracy_score", 0.0),
        "preferences": UserPreferences(**user_data.get("preferences", {})),
        "created_at": user_data.get("created_at", now),
        "last_login": now,
        "updated_at": now
    }
    
    return UserProfile(**profile_data)

# ============== FIREBASE AUTHENTICATION ==============

@router.post("/firebase-login", response_model=OAuthResponse)
async def firebase_login(request: FirebaseLoginRequest):
    """
    Firebase authentication endpoint - main authentication method per roadmap.
    """
    try:
        logger.info("Firebase login attempt")
        
        # Verify Firebase token
        if settings.use_mocks:
            # Mock verification for development
            firebase_user = {
                "uid": f"firebase_{uuid.uuid4().hex[:8]}",
                "email": request.user.get("email", "user@example.com") if request.user else "user@example.com",
                "name": request.user.get("displayName", "Firebase User") if request.user else "Firebase User",
                "picture": request.user.get("photoURL") if request.user else None,
                "email_verified": True
            }
        else:
            firebase_user = await verify_firebase_token(request.idToken)
        
        # Check if user exists
        user_id = firebase_user["uid"]
        is_new_user = user_id not in users_db
        
        if is_new_user:
            # Create new user profile
            user_data = {
                "id": user_id,
                "email": firebase_user["email"],
                "full_name": firebase_user.get("name", "User"),
                "photo_url": firebase_user.get("picture"),
                "provider": "firebase",
                "email_verified": firebase_user.get("email_verified", True),
                "created_at": datetime.utcnow()
            }
            users_db[user_id] = user_data
            logger.info(f"Created new Firebase user: {user_id}")
        else:
            # Update existing user
            users_db[user_id]["last_login"] = datetime.utcnow()
            users_db[user_id]["updated_at"] = datetime.utcnow()
        
        # Create user profile
        user_profile = create_user_profile(users_db[user_id])
        
        # Generate tokens
        access_token = create_access_token(user_profile.dict())
        refresh_token = create_refresh_token(user_id)
        
        return OAuthResponse(
            token=access_token,
            user=user_profile,
            is_new_user=is_new_user
        )
        
    except Exception as e:
        logger.error(f"Firebase authentication error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Authentication failed: {str(e)}"
        )

# ============== GOOGLE OAUTH ==============

@router.post("/oauth/google", response_model=OAuthResponse)
async def google_oauth_login(request: GoogleOAuthRequest):
    """
    Google OAuth login - secondary authentication method per roadmap.
    """
    try:
        logger.info("Google OAuth login attempt")
        
        if settings.use_mocks:
            # Mock Google user for development
            google_user = {
                "id": f"google_{uuid.uuid4().hex[:8]}",
                "email": "user@gmail.com",
                "name": "Google User",
                "picture": "https://lh3.googleusercontent.com/a/default-user",
                "verified_email": True
            }
        else:
            # In production, verify Google ID token here
            # For now, use mock data
            google_user = {
                "id": f"google_{uuid.uuid4().hex[:8]}",
                "email": "user@gmail.com", 
                "name": "Google User",
                "picture": "https://lh3.googleusercontent.com/a/default-user",
                "verified_email": True
            }
        
        # Check if user exists
        user_id = f"google_{google_user['id']}"
        is_new_user = user_id not in users_db
        
        if is_new_user:
            # Create new user profile
            user_data = {
                "id": user_id,
                "email": google_user["email"],
                "full_name": google_user["name"],
                "photo_url": google_user["picture"],
                "provider": "google",
                "email_verified": google_user["verified_email"],
                "created_at": datetime.utcnow()
            }
            users_db[user_id] = user_data
            logger.info(f"Created new Google user: {user_id}")
        else:
            # Update existing user
            users_db[user_id]["last_login"] = datetime.utcnow()
            users_db[user_id]["updated_at"] = datetime.utcnow()
        
        # Create user profile
        user_profile = create_user_profile(users_db[user_id])
        
        # Generate tokens
        access_token = create_access_token(user_profile.dict())
        refresh_token = create_refresh_token(user_id)
        
        return OAuthResponse(
            token=access_token,
            user=user_profile,
            is_new_user=is_new_user
        )
        
    except Exception as e:
        logger.error(f"Google OAuth error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"OAuth authentication failed: {str(e)}"
        )

# ============== GITHUB OAUTH ==============

@router.post("/oauth/github", response_model=OAuthResponse)
async def github_oauth_login(request: GitHubOAuthRequest):
    """
    GitHub OAuth login - tertiary authentication method per roadmap.
    """
    try:
        logger.info("GitHub OAuth login attempt")
        
        # Get GitHub user info
        if request.accessToken:
            github_user = await get_github_user_info(request.accessToken)
        else:
            # Handle OAuth code flow in production
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Access token required"
            )
        
        # Check if user exists
        user_id = f"github_{github_user['id']}"
        is_new_user = user_id not in users_db
        
        if is_new_user:
            # Create new user profile
            user_data = {
                "id": user_id,
                "email": github_user.get("email", f"github_{github_user['id']}@users.noreply.github.com"),
                "full_name": github_user.get("name", github_user.get("login", "GitHub User")),
                "photo_url": github_user.get("avatar_url"),
                "provider": "github",
                "email_verified": bool(github_user.get("email")),
                "created_at": datetime.utcnow()
            }
            users_db[user_id] = user_data
            logger.info(f"Created new GitHub user: {user_id}")
        else:
            # Update existing user
            users_db[user_id]["last_login"] = datetime.utcnow()
            users_db[user_id]["updated_at"] = datetime.utcnow()
        
        # Create user profile
        user_profile = create_user_profile(users_db[user_id])
        
        # Generate tokens
        access_token = create_access_token(user_profile.dict())
        refresh_token = create_refresh_token(user_id)
        
        return OAuthResponse(
            token=access_token,
            user=user_profile,
            is_new_user=is_new_user
        )
        
    except Exception as e:
        logger.error(f"GitHub OAuth error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"OAuth authentication failed: {str(e)}"
        )

# ============== EMAIL/PASSWORD AUTHENTICATION ==============

@router.post("/register", response_model=OAuthResponse)
async def register_user(request: RegisterRequest):
    """
    Email/password registration - backup authentication method per roadmap.
    """
    try:
        logger.info(f"User registration attempt for email: {request.email}")
        
        # Check if user already exists
        existing_user = None
        for user_data in users_db.values():
            if user_data.get("email") == request.email:
                existing_user = user_data
                break
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create new user
        user_id = f"email_{uuid.uuid4().hex[:8]}"
        hashed_password = hash_password(request.password)
        
        user_data = {
            "id": user_id,
            "email": request.email,
            "full_name": request.full_name,
            "password_hash": hashed_password,
            "provider": "email",
            "email_verified": False,  # Require email verification
            "preferences": {
                "language": request.language_preference
            },
            "created_at": datetime.utcnow()
        }
        
        users_db[user_id] = user_data
        logger.info(f"Created new email user: {user_id}")
        
        # Create user profile
        user_profile = create_user_profile(user_data)
        
        # Generate tokens
        access_token = create_access_token(user_profile.dict())
        refresh_token = create_refresh_token(user_id)
        
        return OAuthResponse(
            token=access_token,
            user=user_profile,
            is_new_user=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )

@router.post("/login", response_model=OAuthResponse)
async def login_user(request: EmailPasswordRequest):
    """
    Email/password login.
    """
    try:
        logger.info(f"Login attempt for email: {request.email}")
        
        # Find user by email
        user_data = None
        for user in users_db.values():
            if user.get("email") == request.email and user.get("provider") == "email":
                user_data = user
                break
        
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Verify password
        if not verify_password(request.password, user_data["password_hash"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Update last login
        user_data["last_login"] = datetime.utcnow()
        user_data["updated_at"] = datetime.utcnow()
        
        # Create user profile
        user_profile = create_user_profile(user_data)
        
        # Generate tokens
        access_token = create_access_token(user_profile.dict())
        refresh_token = create_refresh_token(user_data["id"])
        
        return OAuthResponse(
            token=access_token,
            user=user_profile,
            is_new_user=False
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )

# ============== USER PROFILE MANAGEMENT ==============

@router.get("/profile", response_model=UserProfile)
async def get_user_profile(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Get current user profile.
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    user_id = current_user.get("uid") or current_user.get("id")
    if user_id in users_db:
        return create_user_profile(users_db[user_id])
    
    # Create profile from Firebase/OAuth data
    user_data = {
        "id": user_id,
        "email": current_user.get("email", "user@example.com"),
        "full_name": current_user.get("name", "User"),
        "photo_url": current_user.get("picture"),
        "provider": "firebase",
        "email_verified": current_user.get("email_verified", True),
        "is_admin": current_user.get("admin", False),
        "created_at": datetime.utcnow()
    }
    
    users_db[user_id] = user_data
    return create_user_profile(user_data)

@router.put("/profile", response_model=UserProfile)
async def update_user_profile(
    request: UserProfileUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Update user profile.
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    user_id = current_user.get("uid") or current_user.get("id")
    
    if user_id not in users_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update user data
    if request.full_name:
        users_db[user_id]["full_name"] = request.full_name
    if request.photo_url:
        users_db[user_id]["photo_url"] = request.photo_url
    if request.preferences:
        users_db[user_id]["preferences"] = request.preferences.dict()
    
    users_db[user_id]["updated_at"] = datetime.utcnow()
    
    return create_user_profile(users_db[user_id])

# ============== TOKEN MANAGEMENT ==============

@router.post("/refresh", response_model=TokenResponse)
async def refresh_access_token(request: RefreshTokenRequest):
    """
    Refresh access token using refresh token.
    """
    try:
        refresh_token = request.refresh_token
        
        if refresh_token not in refresh_tokens:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        token_data = refresh_tokens[refresh_token]
        
        # Check if token is expired
        if datetime.utcnow() > token_data["expires_at"]:
            del refresh_tokens[refresh_token]
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token expired"
            )
        
        # Get user data
        user_id = token_data["user_id"]
        if user_id not in users_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        user_profile = create_user_profile(users_db[user_id])
        
        # Generate new access token
        access_token = create_access_token(user_profile.dict())
        new_refresh_token = create_refresh_token(user_id)
        
        # Remove old refresh token
        del refresh_tokens[refresh_token]
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=86400,  # 24 hours
            refresh_token=new_refresh_token
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed"
        )

@router.post("/logout")
async def logout_user(
    refresh_token: Optional[str] = None,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Logout user by invalidating tokens.
    """
    try:
        # Remove refresh token if provided
        if refresh_token and refresh_token in refresh_tokens:
            del refresh_tokens[refresh_token]
        
        # In production, you would also invalidate the access token
        # by adding it to a blacklist or revoking it
        
        return {"message": "Successfully logged out"}
        
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        return {"message": "Logout completed with warnings"}

# ============== GUEST SESSION UPGRADE ==============

@router.post("/upgrade-guest", response_model=OAuthResponse)
async def upgrade_guest_session(request: GuestUpgradeRequest):
    """
    Upgrade guest session to authenticated user - ChatGPT style migration.
    """
    try:
        logger.info(f"Upgrading guest session: {request.guest_id}")
        
        # Authenticate the user first
        auth_data = request.auth_request
        
        if "idToken" in auth_data:
            # Firebase authentication
            firebase_req = FirebaseLoginRequest(**auth_data)
            auth_response = await firebase_login(firebase_req)
        elif "accessToken" in auth_data:
            # GitHub OAuth
            github_req = GitHubOAuthRequest(**auth_data)
            auth_response = await github_oauth_login(github_req)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid authentication data"
            )
        
        # Here you would migrate guest session data to the authenticated user
        # For now, just return the authentication response with upgrade message
        
        logger.info(f"Successfully upgraded guest {request.guest_id} to user {auth_response.user.id}")
        
        return OAuthResponse(
            token=auth_response.token,
            user=auth_response.user,
            is_new_user=auth_response.is_new_user
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Guest upgrade error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Guest upgrade failed"
        )

# ============== ADMIN ENDPOINTS ==============

@router.post("/admin/manage-user")
async def admin_manage_user(
    request: AdminUserRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Admin endpoint for managing users.
    """
    if not current_user or not current_user.get("admin", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    target_user_id = request.user_id
    
    if target_user_id not in users_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Perform admin action
    if request.action == "promote":
        users_db[target_user_id]["role"] = "admin"
        users_db[target_user_id]["is_admin"] = True
    elif request.action == "demote":
        users_db[target_user_id]["role"] = "user"
        users_db[target_user_id]["is_admin"] = False
    elif request.action == "ban":
        users_db[target_user_id]["banned"] = True
    elif request.action == "unban":
        users_db[target_user_id]["banned"] = False
    elif request.action == "verify_email":
        users_db[target_user_id]["email_verified"] = True
    
    users_db[target_user_id]["updated_at"] = datetime.utcnow()
    
    logger.info(f"Admin {current_user.get('email')} performed {request.action} on user {target_user_id}")
    
    return {
        "message": f"Successfully performed {request.action} on user",
        "user_id": target_user_id,
        "action": request.action,
        "reason": request.reason
    }

# Health check
@router.get("/health")
async def auth_health_check():
    """Health check for authentication service."""
    return {
        "status": "healthy",
        "registered_users": len(users_db),
        "active_refresh_tokens": len(refresh_tokens),
        "timestamp": datetime.utcnow()
    }
