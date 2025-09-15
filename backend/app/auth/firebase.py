"""
Authentication utilities for Firebase and JWT.
"""
import logging
from typing import Optional, Dict, Any
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from app.core.config import settings
import firebase_admin
from firebase_admin import credentials, auth
import httpx

logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

# Initialize Firebase Admin SDK
try:
    if settings.USE_MOCKS:
        logger.warning("Firebase Admin SDK is not initialized in mock mode.")
        cred = None
    elif settings.FIREBASE_PRIVATE_KEY:
        logger.info("Initializing Firebase Admin SDK from environment variables...")
        # Sanitize private key
        private_key = settings.FIREBASE_PRIVATE_KEY.replace('\\n', '\n')
        
        cred_json = {
            "type": "service_account",
            "project_id": settings.FIREBASE_PROJECT_ID,
            "private_key_id": settings.FIREBASE_PRIVATE_KEY_ID,
            "private_key": private_key,
            "client_email": settings.FIREBASE_CLIENT_EMAIL,
            "client_id": settings.FIREBASE_CLIENT_ID,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": f"https://www.googleapis.com/robot/v1/metadata/x509/{settings.FIREBASE_CLIENT_EMAIL}"
        }
        cred = credentials.Certificate(cred_json)
    elif settings.GOOGLE_APPLICATION_CREDENTIALS:
        logger.info(f"Initializing Firebase Admin SDK from file: {settings.GOOGLE_APPLICATION_CREDENTIALS}")
        cred = credentials.Certificate(settings.GOOGLE_APPLICATION_CREDENTIALS)
    else:
        cred = None
        logger.warning("Firebase credentials not found. Firebase features will be disabled.")

    if cred:
        firebase_admin.initialize_app(cred)
        logger.info("Firebase Admin SDK initialized successfully.")

except Exception as e:
    logger.error(f"Failed to initialize Firebase Admin SDK: {e}")
    # Allow the application to continue running without Firebase features
    firebase_admin._apps.clear()


async def verify_firebase_token(id_token: str) -> dict:
    """
    Verify Firebase ID token and return user information.
    """
    if settings.USE_MOCKS:
        logger.info("Skipping Firebase token verification in mock mode.")
        return {
            "uid": "mock_user_123",
            "email": "mock@example.com",
            "name": "Mock User",
            "picture": "https://via.placeholder.com/150",
            "email_verified": True
        }
    try:
        decoded_token = auth.verify_id_token(id_token)
        return decoded_token
    except auth.ExpiredIdTokenError:
        raise HTTPException(status_code=401, detail="Firebase token has expired")
    except auth.InvalidIdTokenError:
        raise HTTPException(status_code=401, detail="Invalid Firebase token")
    except Exception as e:
        logger.error(f"Firebase token verification failed: {e}")
        raise HTTPException(status_code=401, detail="Could not verify Firebase token")


async def get_current_user(token: str = Depends(oauth2_scheme)) -> Dict[str, Any]:
    """

    Decode JWT token to get current user.
    This function can be used as a dependency in FastAPI endpoints.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
            audience=settings.JWT_AUDIENCE
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        
        # In a real app, you might fetch user details from a database here
        # For now, we'll just return the payload
        return payload

    except JWTError:
        # Fallback to Firebase token verification for backward compatibility
        try:
            return await verify_firebase_token(token)
        except HTTPException:
            raise credentials_exception


def require_auth(required_role: Optional[str] = None):
    """
    Dependency to protect endpoints that require authentication.
    Optionally checks for a specific user role.
    """
    async def _require_auth(current_user: dict = Depends(get_current_user)):
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated"
            )
        
        if required_role:
            user_roles = current_user.get("roles", [])
            if required_role not in user_roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"User does not have the required '{required_role}' role"
                )
        
        return current_user
    
    return _require_auth


def require_roles(*roles: str):
    """
    Dependency to protect endpoints that require specific roles.
    Usage: require_roles("admin", "moderator")
    """
    def _require_roles(current_user: dict = Depends(get_current_user)):
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated"
            )
        
        user_roles = current_user.get("roles", [])
        user_role = current_user.get("role", "user")
        
        # Check if user has any of the required roles
        if not any(role in user_roles or role == user_role for role in roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"User does not have any of the required roles: {', '.join(roles)}"
            )
        
        return current_user
    
    return _require_roles


def require_admin(current_user: dict = Depends(get_current_user)):
    """
    Dependency to protect endpoints that require admin privileges.
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    if not current_user.get("admin", False) and not current_user.get("is_admin", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User does not have admin privileges"
        )
    
    return current_user


async def set_admin_claim(user_id: str, is_admin: bool):
    """
    Set custom admin claim for a user in Firebase.
    """
    if settings.USE_MOCKS:
        logger.info(f"Mock: Setting admin claim for {user_id} to {is_admin}")
        return True
    try:
        auth.set_custom_user_claims(user_id, {'admin': is_admin})
        logger.info(f"Successfully set admin claim for user {user_id} to {is_admin}")
        return True
    except Exception as e:
        logger.error(f"Failed to set admin claim for user {user_id}: {e}")
        return False


async def get_github_user_info(access_token: str) -> dict:
    """
    Get user information from GitHub using an access token.
    """
    headers = {"Authorization": f"token {access_token}"}
    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.github.com/user", headers=headers)
        response.raise_for_status()
        return response.json()
