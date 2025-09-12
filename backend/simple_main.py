#!/usr/bin/env python3
"""
ChatGPT-style authentication backend with guest access
"""
import os
import uvicorn
from fastapi import FastAPI, HTTPException, Request, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List, Union
import logging
import uuid
import json
import random
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="MisinfoGuard API - ChatGPT Style Auth",
    description="ChatGPT-style authentication with guest access",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001", "http://127.0.0.1:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for demo purposes
guest_sessions = {}
users_db = {}

# Pydantic models
class FirebaseLoginRequest(BaseModel):
    idToken: str
    user: Optional[Dict[str, Any]] = None

class GoogleOAuthRequest(BaseModel):
    idToken: str

class OAuthResponse(BaseModel):
    token: str
    user: Dict[str, Any]

class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    photoUrl: Optional[str] = None
    isAdmin: bool = False
    points: int = 0
    level: int = 1

class CheckRequest(BaseModel):
    inputType: str
    payload: str
    language: Optional[str] = "auto"
    userContext: Optional[Dict[str, Any]] = None

class CheckResponse(BaseModel):
    id: str
    score: float
    badge: str
    verdict: str
    summary: str
    reasoning: str
    metadata: Dict[str, Any]

class UserProfileResponse(BaseModel):
    id: str
    email: str
    full_name: str
    photoUrl: Optional[str] = None
    isAdmin: bool = False
    points: int = 0
    level: int = 1
    provider: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None

class UserProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None
    upgrade_prompt: Optional[Dict[str, Any]] = None

@app.get("/")
async def root():
    return {"message": "MisinfoGuard API - ChatGPT Style Authentication", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "API is running"}

# ============== FIREBASE AUTHENTICATION (Like ChatGPT) ==============

@app.post("/api/v1/auth/firebase-login", response_model=OAuthResponse)
async def firebase_login(request: FirebaseLoginRequest):
    """
    Firebase authentication endpoint - similar to ChatGPT's auth
    """
    try:
        logger.info(f"Firebase login attempt with token: {request.idToken[:20]}...")
        
        # In real implementation, verify Firebase ID token
        # For demo, extract user info from request
        user_data = request.user or {}
        
        # Create user profile
        user_profile = {
            "id": user_data.get("uid", f"firebase_{uuid.uuid4().hex[:8]}"),
            "email": user_data.get("email", "user@example.com"),
            "full_name": user_data.get("displayName", "User"),
            "photoUrl": user_data.get("photoURL"),
            "isAdmin": False,
            "points": 0,
            "level": 1,
            "provider": "firebase",
            "preferences": {
                "language": "en",
                "notifications": True,
                "privacyLevel": "public"
            }
        }
        
        # Store user
        users_db[user_profile["id"]] = user_profile
        
        # Generate token
        token = f"firebase_token_{user_profile['id']}_{uuid.uuid4().hex[:8]}"
        
        logger.info(f"Successfully authenticated Firebase user: {user_profile['email']}")
        
        return OAuthResponse(
            token=token,
            user=user_profile
        )
        
    except Exception as e:
        logger.error(f"Firebase authentication error: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Authentication failed: {str(e)}")

# ============== GOOGLE OAUTH (ChatGPT Style) ==============

@app.post("/api/v1/auth/oauth/google", response_model=OAuthResponse)
async def google_oauth_login(request: GoogleOAuthRequest):
    """
    Google OAuth login - ChatGPT style
    """
    try:
        logger.info(f"Google OAuth login attempt")
        
        # Mock Google user verification
        user_profile = {
            "id": f"google_{uuid.uuid4().hex[:8]}",
            "email": "user@gmail.com",
            "full_name": "Google User",
            "photoUrl": "https://lh3.googleusercontent.com/a/default-user",
            "isAdmin": False,
            "points": 0,
            "level": 1,
            "provider": "google",
            "preferences": {
                "language": "en",
                "notifications": True,
                "privacyLevel": "public"
            }
        }
        
        # Store user
        users_db[user_profile["id"]] = user_profile
        
        # Generate token
        token = f"google_token_{user_profile['id']}_{uuid.uuid4().hex[:8]}"
        
        logger.info(f"Successfully authenticated Google user: {user_profile['email']}")
        
        return OAuthResponse(
            token=token,
            user=user_profile
        )
        
    except Exception as e:
        logger.error(f"Google OAuth error: {str(e)}")
        raise HTTPException(status_code=400, detail=f"OAuth authentication failed: {str(e)}")

# ============== GUEST ACCESS (Like ChatGPT's Try Mode) ==============

def get_or_create_guest_session(guest_id: Optional[str] = None) -> Dict[str, Any]:
    """Get or create guest session"""
    if not guest_id:
        guest_id = f"guest_{uuid.uuid4().hex[:12]}"
    
    if guest_id not in guest_sessions:
        guest_sessions[guest_id] = {
            "id": guest_id,
            "created_at": datetime.utcnow().isoformat(),
            "last_activity": datetime.utcnow().isoformat(),
            "checks_count": 0,
            "daily_limit": 10,
            "history": []
        }
    
    guest_sessions[guest_id]["last_activity"] = datetime.utcnow().isoformat()
    return guest_sessions[guest_id]

@app.post("/api/v1/guest/check", response_model=CheckResponse)
async def guest_fact_check(
    request: CheckRequest,
    guest_id: Optional[str] = Header(None, alias="X-Guest-ID")
):
    """
    Guest fact checking - like ChatGPT's free tier
    """
    try:
        session = get_or_create_guest_session(guest_id)
        
        # Check rate limit
        if session["checks_count"] >= session["daily_limit"]:
            raise HTTPException(
                status_code=429,
                detail={
                    "message": "Daily limit reached. Sign up for unlimited access!",
                    "limit": session["daily_limit"],
                    "upgrade_url": "/auth/register"
                }
            )
        
        # Mock fact check analysis
        check_id = f"check_{uuid.uuid4().hex[:8]}"
        
        # Simple mock analysis based on content
        content = request.payload.lower()
        if any(word in content for word in ["fake", "false", "lie", "hoax"]):
            score = 0.2
            badge = "red"
            verdict = "Likely Misinformation"
        elif any(word in content for word in ["true", "verified", "confirmed"]):
            score = 0.9
            badge = "green"
            verdict = "Likely Accurate"
        else:
            score = 0.6
            badge = "yellow"
            verdict = "Needs Verification"
        
        # Update session
        session["checks_count"] += 1
        session["history"].append({
            "id": check_id,
            "timestamp": datetime.utcnow().isoformat(),
            "verdict": verdict
        })
        
        # Create response
        response_data = {
            "id": check_id,
            "score": score,
            "badge": badge,
            "verdict": verdict,
            "summary": f"Analysis of {request.inputType} content shows {verdict.lower()}",
            "reasoning": "This is a demo analysis. In production, this would use advanced AI models.",
            "metadata": {
                "processingTime": 1.2,
                "language": request.language or "en",
                "modelVersion": "demo-v1",
                "timestamp": datetime.utcnow().isoformat(),
                "is_guest": True,
                "remaining_checks": session["daily_limit"] - session["checks_count"],
                "guest_id": session["id"]
            }
        }
        
        # Add upgrade prompt when getting close to limit
        if session["checks_count"] >= session["daily_limit"] * 0.7:  # 70% of limit
            response_data["upgrade_prompt"] = {
                "message": "You're running low on free checks!",
                "benefits": [
                    "Unlimited fact checking",
                    "Detailed analysis with sources",
                    "Save and share results",
                    "Advanced AI models"
                ],
                "cta_url": "/auth/register"
            }
        
        logger.info(f"Guest check completed. Remaining: {response_data['metadata']['remaining_checks']}")
        
        return CheckResponse(**response_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Guest fact check error: {str(e)}")
        raise HTTPException(status_code=500, detail="Analysis failed")

@app.get("/api/v1/guest/session")
async def get_guest_session(guest_id: Optional[str] = Header(None, alias="X-Guest-ID")):
    """Get guest session info"""
    if not guest_id or guest_id not in guest_sessions:
        raise HTTPException(status_code=404, detail="Guest session not found")
    
    session = guest_sessions[guest_id]
    return {
        "guest_id": session["id"],
        "checks_remaining": session["daily_limit"] - session["checks_count"],
        "daily_limit": session["daily_limit"],
        "history_count": len(session["history"]),
        "created_at": session["created_at"]
    }

@app.get("/api/v1/guest/limits")
async def get_guest_limits():
    """Get guest limitations info"""
    return {
        "daily_check_limit": 10,
        "features": {
            "basic_fact_checking": True,
            "quick_analysis": True,
            "unlimited_checks": False,
            "detailed_reports": False,
            "save_results": False,
            "history_tracking": False
        },
        "upgrade_benefits": [
            "Unlimited daily fact checks",
            "Advanced AI analysis",
            "Detailed source verification", 
            "Save and organize results",
            "Share findings with others",
            "Personal dashboard",
            "Priority processing"
        ]
    }

@app.post("/api/v1/auth/oauth/google", response_model=OAuthResponse)
async def google_oauth_login(request: GoogleOAuthRequest):
    """
    Google OAuth login endpoint
    """
    try:
        logger.info(f"Received Google OAuth request with ID token: {request.idToken[:20]}...")
        
        # In a real implementation, you would:
        # 1. Verify the ID token with Google
        # 2. Extract user information
        # 3. Create or update user in database
        # 4. Generate JWT token for your app
        
        # For testing purposes, we'll return mock data
        mock_user = {
            "id": "google_123456",
            "email": "test.user@gmail.com",
            "full_name": "Test User",
            "photoUrl": "https://lh3.googleusercontent.com/a/default-user",
            "isAdmin": False,
            "points": 0,
            "level": 1,
            "preferences": {
                "language": "en",
                "notifications": True,
                "privacyLevel": "public"
            }
        }
        
        # Generate mock JWT token
        mock_token = f"mock_jwt_token_for_google_user_{mock_user['id']}"
        
        logger.info(f"Successfully authenticated user: {mock_user['email']}")
        
        return OAuthResponse(
            token=mock_token,
            user=mock_user
        )
        
    except Exception as e:
        logger.error(f"Error in Google OAuth: {str(e)}")
        raise HTTPException(status_code=400, detail=f"OAuth authentication failed: {str(e)}")

@app.post("/api/v1/auth/oauth/github", response_model=OAuthResponse)
async def github_oauth_login(request: dict):
    """
    GitHub OAuth login endpoint
    """
    try:
        access_token = request.get("accessToken")
        if not access_token:
            raise HTTPException(status_code=400, detail="Access token is required")
            
        logger.info(f"Received GitHub OAuth request with access token: {access_token[:20]}...")
        
        # Mock GitHub user
        mock_user = {
            "id": "github_789123",
            "email": "test.user@github.com",
            "full_name": "GitHub Test User",
            "photoUrl": "https://avatars.githubusercontent.com/u/123456",
            "isAdmin": False,
            "points": 0,
            "level": 1,
            "preferences": {
                "language": "en",
                "notifications": True,
                "privacyLevel": "public"
            }
        }
        
        # Generate mock JWT token
        mock_token = f"mock_jwt_token_for_github_user_{mock_user['id']}"
        
        logger.info(f"Successfully authenticated user: {mock_user['email']}")
        
        return OAuthResponse(
            token=mock_token,
            user=mock_user
        )
        
    except Exception as e:
        logger.error(f"Error in GitHub OAuth: {str(e)}")
        raise HTTPException(status_code=400, detail=f"OAuth authentication failed: {str(e)}")

@app.get("/api/v1/auth/profile", response_model=UserResponse)
async def get_user_profile(request: Request):
    """
    Get user profile from JWT token
    """
    try:
        # Extract authorization header
        auth_header = request.headers.get("authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Authorization header required")
        
        token = auth_header.split(" ")[1]
        logger.info(f"Getting profile for token: {token[:20]}...")
        
        # Mock user profile based on token
        if "google" in token:
            user_data = {
                "id": "google_123456",
                "email": "test.user@gmail.com",
                "full_name": "Test User",
                "photoUrl": "https://lh3.googleusercontent.com/a/default-user",
                "isAdmin": False,
                "points": 0,
                "level": 1
            }
        elif "github" in token:
            user_data = {
                "id": "github_789123",
                "email": "test.user@github.com",
                "full_name": "GitHub Test User", 
                "photoUrl": "https://avatars.githubusercontent.com/u/123456",
                "isAdmin": False,
                "points": 0,
                "level": 1
            }
        else:
            user_data = {
                "id": "test_user_123",
                "email": "test@example.com",
                "full_name": "Test User",
                "photoUrl": None,
                "isAdmin": False,
                "points": 0,
                "level": 1
            }
        
        return UserResponse(**user_data)
        
    except Exception as e:
        logger.error(f"Error getting user profile: {str(e)}")
        raise HTTPException(status_code=401, detail="Invalid token")

@app.post("/api/v1/auth/refresh-token")
async def refresh_token(request: Request):
    """
    Refresh JWT token
    """
    try:
        auth_header = request.headers.get("authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Authorization header required")
        
        old_token = auth_header.split(" ")[1]
        logger.info(f"Refreshing token: {old_token[:20]}...")
        
        # Generate new mock token
        new_token = f"refreshed_{old_token}"
        
        return {
            "token": new_token,
            "message": "Token refreshed successfully"
        }
        
    except Exception as e:
        logger.error(f"Error refreshing token: {str(e)}")
        raise HTTPException(status_code=401, detail="Token refresh failed")

# ============== USER AUTHENTICATION & PROFILE ==============

async def get_current_user(authorization: Optional[str] = Header(None)) -> Dict[str, Any]:
    """Get current authenticated user - ChatGPT style"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    token = authorization.split(" ")[1]
    
    # Find user by token (simple lookup)
    for user_id, user in users_db.items():
        if token.endswith(user_id[-8:]):  # Match last 8 chars of user ID
            return user
    
    raise HTTPException(status_code=401, detail="Invalid token")

@app.get("/api/v1/user/profile", response_model=UserProfileResponse)
async def get_user_profile_v2(current_user = Depends(get_current_user)):
    """Get user profile"""
    return UserProfileResponse(**current_user)

@app.put("/api/v1/user/profile", response_model=UserProfileResponse)
async def update_user_profile(
    profile_update: UserProfileUpdate,
    current_user = Depends(get_current_user)
):
    """Update user profile"""
    user_id = current_user["id"]
    
    # Update user data
    if profile_update.full_name:
        users_db[user_id]["full_name"] = profile_update.full_name
    if profile_update.preferences:
        users_db[user_id]["preferences"].update(profile_update.preferences)
    
    return UserProfileResponse(**users_db[user_id])

@app.post("/api/v1/user/upgrade")
async def upgrade_guest_to_user(
    auth_request: Union[FirebaseLoginRequest, GoogleOAuthRequest],
    guest_id: Optional[str] = Header(None, alias="X-Guest-ID")
):
    """
    Convert guest session to authenticated user - ChatGPT style
    """
    try:
        # Authenticate user based on request type
        if hasattr(auth_request, 'idToken'):  # Firebase
            auth_response = await firebase_login(auth_request)
        else:  # Google OAuth
            auth_response = await google_oauth_login(auth_request)
        
        # Migrate guest data if exists
        if guest_id and guest_id in guest_sessions:
            guest_session = guest_sessions[guest_id]
            user_id = auth_response.user["id"]
            
            # Transfer guest history to user
            users_db[user_id]["guest_migration"] = {
                "previous_checks": guest_session["checks_count"],
                "history": guest_session["history"],
                "migrated_at": datetime.utcnow().isoformat()
            }
            
            # Clean up guest session
            del guest_sessions[guest_id]
            
            logger.info(f"Successfully migrated guest {guest_id} to user {user_id}")
        
        return {
            "message": "Successfully upgraded to full account!",
            "user": auth_response.user,
            "token": auth_response.token,
            "benefits_unlocked": [
                "Unlimited fact checking",
                "Detailed analysis reports",
                "Save and organize results",
                "Personal dashboard"
            ]
        }
        
    except Exception as e:
        logger.error(f"User upgrade error: {str(e)}")
        raise HTTPException(status_code=400, detail="Upgrade failed")

# ============== FACT CHECKING FOR AUTHENTICATED USERS ==============

@app.post("/api/v1/check", response_model=CheckResponse)
async def authenticated_fact_check(
    request: CheckRequest,
    current_user = Depends(get_current_user)
):
    """
    Full fact checking for authenticated users
    """
    try:
        check_id = f"check_{uuid.uuid4().hex[:8]}"
        
        # Enhanced analysis for authenticated users
        content = request.payload.lower()
        
        # More sophisticated mock analysis
        analysis_result = {
            "score": random.uniform(0.1, 0.9),
            "confidence": random.uniform(0.7, 0.95),
            "sources_found": random.randint(3, 15),
            "cross_references": random.randint(1, 8)
        }
        
        if analysis_result["score"] < 0.3:
            badge = "red"
            verdict = "Likely Misinformation"
        elif analysis_result["score"] > 0.7:
            badge = "green" 
            verdict = "Likely Accurate"
        else:
            badge = "yellow"
            verdict = "Needs Further Verification"
        
        # Store check in user history
        if "check_history" not in users_db[current_user["id"]]:
            users_db[current_user["id"]]["check_history"] = []
        
        check_record = {
            "id": check_id,
            "timestamp": datetime.utcnow().isoformat(),
            "input_type": request.inputType,
            "verdict": verdict,
            "score": analysis_result["score"],
            "content_preview": request.payload[:100] + "..." if len(request.payload) > 100 else request.payload
        }
        
        users_db[current_user["id"]]["check_history"].append(check_record)
        
        # Update user points
        users_db[current_user["id"]]["points"] += 10
        
        response_data = {
            "id": check_id,
            "score": analysis_result["score"],
            "badge": badge,
            "verdict": verdict,
            "summary": f"Comprehensive analysis of {request.inputType} content indicates {verdict.lower()}",
            "reasoning": f"Based on {analysis_result['sources_found']} sources and {analysis_result['cross_references']} cross-references with {analysis_result['confidence']:.0%} confidence.",
            "metadata": {
                "processingTime": random.uniform(2.1, 4.8),
                "language": request.language or "en",
                "modelVersion": "advanced-v2.1",
                "timestamp": datetime.utcnow().isoformat(),
                "is_guest": False,
                "user_id": current_user["id"],
                "confidence": analysis_result["confidence"],
                "sources_analyzed": analysis_result["sources_found"]
            }
        }
        
        logger.info(f"Authenticated fact check completed for user {current_user['id']}")
        
        return CheckResponse(**response_data)
        
    except Exception as e:
        logger.error(f"Authenticated fact check error: {str(e)}")
        raise HTTPException(status_code=500, detail="Analysis failed")

@app.get("/api/v1/user/history")
async def get_user_history(
    limit: int = 20,
    offset: int = 0,
    current_user = Depends(get_current_user)
):
    """Get user's fact check history"""
    history = users_db[current_user["id"]].get("check_history", [])
    
    # Sort by timestamp (newest first)
    sorted_history = sorted(history, key=lambda x: x["timestamp"], reverse=True)
    
    # Apply pagination
    paginated_history = sorted_history[offset:offset + limit]
    
    return {
        "history": paginated_history,
        "total": len(history),
        "limit": limit,
        "offset": offset,
        "has_more": offset + limit < len(history)
    }

# ============== TOKEN REFRESH & SESSION MANAGEMENT ==============

@app.post("/api/v1/auth/refresh")
async def refresh_token_v2(current_user = Depends(get_current_user)):
    """Refresh authentication token - ChatGPT style"""
    try:
        # Generate new token
        new_token = f"{current_user['provider']}_token_{current_user['id']}_{uuid.uuid4().hex[:8]}"
        
        # Update last activity
        users_db[current_user["id"]]["last_activity"] = datetime.utcnow().isoformat()
        
        return {
            "token": new_token,
            "expires_in": 86400,  # 24 hours
            "user": current_user
        }
        
    except Exception as e:
        logger.error(f"Token refresh error: {str(e)}")
        raise HTTPException(status_code=400, detail="Token refresh failed")

@app.post("/api/v1/auth/logout")
async def logout(current_user = Depends(get_current_user)):
    """Logout user"""
    # In a real app, invalidate the token
    # For demo, just return success
    return {
        "message": "Successfully logged out",
        "user_id": current_user["id"]
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "simple_main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )
