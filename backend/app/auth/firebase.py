"""
Firebase authentication utilities for token verification.
"""
import logging
from typing import Optional, Dict, Any
import firebase_admin
from firebase_admin import auth, credentials
from fastapi import HTTPException, Header
from app.core.config import settings

logger = logging.getLogger(__name__)

# Initialize Firebase Admin SDK
try:
    if settings.use_mocks:
        logger.info("Using Firebase mocks for development")
        firebase_app = None
    else:
        if settings.google_application_credentials:
            cred = credentials.Certificate(settings.google_application_credentials)
        else:
            # Use default credentials
            cred = credentials.ApplicationDefault()
        
        firebase_app = firebase_admin.initialize_app(cred, {
            'projectId': settings.google_project_id,
        })
        logger.info("Firebase Admin SDK initialized")
except Exception as e:
    logger.warning(f"Firebase initialization failed: {e}")
    firebase_app = None


async def verify_firebase_token(id_token: str) -> Dict[str, Any]:
    """
    Verify Firebase ID token and return user claims.
    
    Args:
        id_token: Firebase ID token from client
        
    Returns:
        Dict containing user information and claims
        
    Raises:
        HTTPException: If token is invalid
    """
    try:
        if settings.use_mocks:
            # Return mock user for development
            return {
                "uid": "mock_user_123",
                "email": "mock@example.com",
                "name": "Mock User",
                "admin": False,
                "email_verified": True
            }
        
        if not firebase_app:
            raise HTTPException(
                status_code=503, 
                detail="Firebase not configured"
            )
        
        # Verify the token
        decoded_token = auth.verify_id_token(id_token)
        
        # Extract user information
        user_info = {
            "uid": decoded_token["uid"],
            "email": decoded_token.get("email"),
            "name": decoded_token.get("name"),
            "picture": decoded_token.get("picture"),
            "email_verified": decoded_token.get("email_verified", False),
            "admin": decoded_token.get("admin", False),  # Custom claim
            "role": decoded_token.get("role", "user"),   # Custom claim
        }
        
        return user_info
        
    except firebase_admin.auth.InvalidIdTokenError:
        raise HTTPException(
            status_code=401, 
            detail="Invalid authentication token"
        )
    except firebase_admin.auth.ExpiredIdTokenError:
        raise HTTPException(
            status_code=401, 
            detail="Authentication token has expired"
        )
    except Exception as e:
        logger.error(f"Token verification error: {e}")
        raise HTTPException(
            status_code=401, 
            detail="Authentication failed"
        )


async def get_current_user(authorization: Optional[str] = Header(None)) -> Optional[Dict[str, Any]]:
    """
    Extract and verify user from Authorization header.
    
    Args:
        authorization: Authorization header (Bearer token)
        
    Returns:
        User information dict or None if no valid token
    """
    if not authorization:
        if settings.use_mocks:
            # For development, return a mock user if no token
            logger.debug("No authorization header, using mock user")
            return {
                "uid": "mock_user_123",
                "email": "mock@example.com",
                "name": "Mock User",
                "admin": False,
                "email_verified": True
            }
        return None
    
    try:
        # Extract token from "Bearer <token>" format
        if not authorization.startswith("Bearer "):
            if settings.use_mocks:
                # For development, be lenient with auth header format
                token = authorization
            else:
                return None
        else:
            token = authorization.split(" ")[1]
            
        # Handle mock token cases specially
        if settings.use_mocks:
            # Check for any of our mock tokens
            if token == "mock-jwt-token-123" or token.startswith("mock-") or token.startswith("refreshed-mock-token"):
                # Check for admin token
                is_admin = "admin" in token
                
                # For admin tokens, return admin user
                if is_admin:
                    return {
                        "uid": "admin_user_456",
                        "email": "admin@example.com",
                        "name": "Admin User",
                        "admin": True,
                        "email_verified": True
                    }
                
                # Otherwise return regular user
                return {
                    "uid": "mock_user_123",
                    "email": "mock@example.com",
                    "name": "Mock User",
                    "admin": False,
                    "email_verified": True
                }
            
            # Handle Google OAuth mock token
            if token == "google-mock-jwt-token" or token.startswith("google-mock"):
                return {
                    "uid": "google_user_789",
                    "email": "google.user@gmail.com",
                    "name": "Google User",
                    "picture": "https://lh3.googleusercontent.com/a/default-user",
                    "admin": False,
                    "email_verified": True
                }
                
            # Handle GitHub OAuth mock token
            if token == "github-mock-jwt-token" or token.startswith("github-"):
                return {
                    "uid": "github_user_456",
                    "email": "github.user@example.com",
                    "name": "GitHub User",
                    "picture": "https://avatars.githubusercontent.com/u/12345678",
                    "admin": False,
                    "email_verified": True,
                    "provider": "github"
                }
                
            # Handle refresh tokens
            if token.startswith("refreshed-token-"):
                # Extract user ID from the token format
                parts = token.split("-")
                if len(parts) >= 3:
                    uid = parts[2]
                    # Return different user info based on UID
                    if uid == "admin_user_456":
                        return {
                            "uid": "admin_user_456",
                            "email": "admin@example.com",
                            "name": "Admin User",
                            "admin": True,
                            "email_verified": True
                        }
                    elif uid == "google_user_789":
                        return {
                            "uid": "google_user_789",
                            "email": "google.user@gmail.com",
                            "name": "Google User",
                            "picture": "https://lh3.googleusercontent.com/a/default-user",
                            "admin": False,
                            "email_verified": True
                        }
                
                # Default to mock user if no specific match
                return {
                    "uid": "mock_user_123",
                    "email": "mock@example.com",
                    "name": "Mock User",
                    "admin": False,
                    "email_verified": True
                }
            
        # Real Firebase verification
        return await verify_firebase_token(token)
        
    except HTTPException:
        # Re-raise authentication errors
        if settings.use_mocks:
            # In development, provide a mock user even on auth errors
            logger.warning("Authentication error but returning mock user in development mode")
            return {
                "uid": "mock_user_123",
                "email": "mock@example.com",
                "name": "Mock User",
                "admin": False,
                "email_verified": True
            }
        raise
    except Exception as e:
        logger.warning(f"Error getting current user: {e}")
        if settings.use_mocks:
            # In development, provide a mock user
            return {
                "uid": "mock_user_123",
                "email": "mock@example.com",
                "name": "Mock User",
                "admin": False,
                "email_verified": True
            }
        return None


async def require_auth(authorization: str = Header(...)) -> Dict[str, Any]:
    """
    Require authentication - raises 401 if not authenticated.
    
    Args:
        authorization: Authorization header (required)
        
    Returns:
        User information dict
        
    Raises:
        HTTPException: If authentication fails
    """
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Invalid authorization header format"
        )
    
    token = authorization.split(" ")[1]
    return await verify_firebase_token(token)


async def require_admin(authorization: str = Header(...)) -> Dict[str, Any]:
    """
    Require admin authentication - raises 403 if not admin.
    
    Args:
        authorization: Authorization header (required)
        
    Returns:
        User information dict
        
    Raises:
        HTTPException: If authentication fails or user is not admin
    """
    user = await require_auth(authorization)
    
    if not user.get("admin", False):
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )
    
    return user


async def set_admin_claim(uid: str, admin: bool = True) -> bool:
    """
    Set admin custom claim for a user.
    
    Args:
        uid: User ID
        admin: Whether to grant admin privileges
        
    Returns:
        True if successful
    """
    try:
        if settings.use_mocks:
            logger.info(f"Mock: Setting admin={admin} for user {uid}")
            return True
        
        if not firebase_app:
            raise Exception("Firebase not configured")
        
        auth.set_custom_user_claims(uid, {"admin": admin, "role": "admin" if admin else "user"})
        logger.info(f"Set admin={admin} for user {uid}")
        return True
        
    except Exception as e:
        logger.error(f"Error setting admin claim: {e}")
        return False


async def create_custom_token(uid: str, claims: Optional[Dict[str, Any]] = None) -> str:
    """
    Create a custom token for a user (for testing/development).
    
    Args:
        uid: User ID
        claims: Additional claims to include
        
    Returns:
        Custom token string
    """
    try:
        if settings.use_mocks:
            return f"mock_token_{uid}"
        
        if not firebase_app:
            raise Exception("Firebase not configured")
        
        return auth.create_custom_token(uid, claims)
        
    except Exception as e:
        logger.error(f"Error creating custom token: {e}")
        raise


async def get_github_user_info(access_token: str) -> Dict[str, Any]:
    """
    Get GitHub user information using an access token.
    
    Args:
        access_token: GitHub OAuth access token
        
    Returns:
        Dict containing GitHub user information
        
    Raises:
        HTTPException: If API call fails
    """
    import aiohttp
    
    try:
        if settings.use_mocks:
            # Return mock GitHub user for development
            import uuid
            user_id = uuid.uuid4().hex[:8]
            return {
                "id": user_id,
                "login": f"github_user_{user_id}",
                "name": "GitHub Mock User",
                "email": "github.user@example.com",
                "avatar_url": "https://avatars.githubusercontent.com/u/12345678",
            }
        
        # Call GitHub API to get user information
        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"token {access_token}",
                "Accept": "application/json"
            }
            
            # Get user profile
            async with session.get("https://api.github.com/user", headers=headers) as response:
                if response.status != 200:
                    error_detail = await response.text()
                    logger.error(f"GitHub API error: {error_detail}")
                    raise HTTPException(status_code=401, detail="Invalid GitHub token")
                
                user_data = await response.json()
                
                # If email is not in profile, try to get email from emails endpoint
                if not user_data.get("email"):
                    async with session.get("https://api.github.com/user/emails", headers=headers) as email_response:
                        if email_response.status == 200:
                            emails = await email_response.json()
                            primary_email = next((email["email"] for email in emails if email.get("primary")), None)
                            if primary_email:
                                user_data["email"] = primary_email
            
            return user_data
            
    except aiohttp.ClientError as e:
        logger.error(f"GitHub API request error: {e}")
        raise HTTPException(status_code=500, detail="Failed to communicate with GitHub")
    except Exception as e:
        logger.error(f"GitHub user info error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get GitHub user info")


# Export public functions
__all__ = [
    "verify_firebase_token",
    "get_current_user", 
    "require_auth",
    "require_admin",
    "set_admin_claim",
    "create_custom_token",
    "get_github_user_info"
]
