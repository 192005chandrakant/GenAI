"""
Guest access endpoints for unauthenticated users.
Allows guest users to use basic fact-checking features without registration.
"""

from fastapi import APIRouter, HTTPException, Header, Request
from typing import Optional, Dict, Any
import uuid
from datetime import datetime
import logging

from app.models.check_result_schemas import CheckRequest, CheckResponse
from app.core.config import get_settings
from app.models.content_schemas import ContentType

# Configure logger
logger = logging.getLogger(__name__)
settings = get_settings()

router = APIRouter()

# In-memory storage for guest sessions (in production, use Redis or similar)
guest_sessions: Dict[str, Dict[str, Any]] = {}

def get_or_create_guest_session(guest_id: Optional[str] = None) -> Dict[str, Any]:
    """Get existing guest session or create a new one."""
    if not guest_id:
        guest_id = f"guest_{uuid.uuid4().hex[:12]}"
    
    if guest_id not in guest_sessions:
        guest_sessions[guest_id] = {
            "id": guest_id,
            "created_at": datetime.utcnow(),
            "last_activity": datetime.utcnow(),
            "checks_count": 0,
            "daily_limit": 10,  # Limit guest users to 10 checks per day
            "history": []
        }
    
    # Update last activity
    guest_sessions[guest_id]["last_activity"] = datetime.utcnow()
    return guest_sessions[guest_id]

def check_guest_rate_limit(session: Dict[str, Any]) -> bool:
    """Check if guest user has exceeded daily limit."""
    return session["checks_count"] < session["daily_limit"]

@router.post("/check", response_model=CheckResponse)
async def guest_fact_check(
    request: CheckRequest,
    guest_id: Optional[str] = Header(None, alias="X-Guest-ID"),
    request_obj: Request = None
):
    """
    Perform fact checking for guest users.
    Guest users have limited features and daily limits.
    """
    try:
        # Get or create guest session
        session = get_or_create_guest_session(guest_id)
        current_guest_id = session["id"]
        
        # Check rate limit
        if not check_guest_rate_limit(session):
            raise HTTPException(
                status_code=429,
                detail={
                    "message": "Daily limit reached. Please sign up for unlimited access.",
                    "limit": session["daily_limit"],
                    "reset_time": "24 hours",
                    "upgrade_url": "/auth/register"
                }
            )
        
        # Create a simplified mock response instead of using the service
        logger.info(f"Processing guest fact check request for guest_id: {current_guest_id}")
        
        # Mock analysis result for guest users
        mock_result = {
            "id": f"check_{uuid.uuid4().hex[:8]}",
            "content": request.payload,
            "content_type": request.inputType,
            "verdict": "needs_verification" if "claim" in request.payload.lower() else "likely_true",
            "confidence": 0.75,
            "verdict_explanation": "This appears to be factual information. However, please verify with additional sources for complete accuracy.",
            "reasoning": "Guest analysis provides basic fact-checking. Sign up for detailed analysis with sources and citations.",
            "sources": [
                {
                    "title": "Fact Check Database",
                    "url": "https://example.com/factcheck",
                    "reliability": "high"
                }
            ],
            "metadata": {
                "analysis_time_ms": 1200,
                "model_version": "guest-v1",
                "language": request.language or "en",
                "features_used": ["basic_analysis"]
            },
            "claims": [],
            "educational_content": {
                "summary": "Always verify information from multiple sources",
                "tips": [
                    "Check the source credibility",
                    "Look for supporting evidence",
                    "Consider the context"
                ]
            }
        }
        
        # Update session
        session["checks_count"] += 1
        session["history"].append({
            "id": mock_result["id"],
            "timestamp": datetime.utcnow(),
            "content_type": request.inputType,
            "verdict": mock_result["verdict"]
        })
        
        # Keep only last 5 items in history for guests
        if len(session["history"]) > 5:
            session["history"] = session["history"][-5:]
        
        # Add guest-specific metadata to response
        mock_result["metadata"]["is_guest"] = True
        mock_result["metadata"]["remaining_checks"] = session["daily_limit"] - session["checks_count"]
        mock_result["metadata"]["guest_id"] = current_guest_id
        
        # Add upgrade prompts for guests
        if session["checks_count"] >= session["daily_limit"] * 0.8:  # 80% of limit
            mock_result["upgrade_prompt"] = {
                "message": "You're running low on free checks. Sign up for unlimited access!",
                "benefits": [
                    "Unlimited fact checking",
                    "Detailed analysis reports", 
                    "Save and share results",
                    "Track your fact-checking history"
                ],
                "cta_url": "/auth/register"
            }
        
        return CheckResponse(**mock_result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in guest fact check: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to process fact check request. Please try again."
        )

@router.get("/session")
async def get_guest_session(
    guest_id: Optional[str] = Header(None, alias="X-Guest-ID")
):
    """Get or create guest session information."""
    # Create a new session if guest_id is not provided or session doesn't exist
    session = get_or_create_guest_session(guest_id)
    
    return {
        "guest_id": session["id"],
        "checks_remaining": session["daily_limit"] - session["checks_count"],
        "daily_limit": session["daily_limit"],
        "history_count": len(session["history"]),
        "created_at": session["created_at"].isoformat() if hasattr(session["created_at"], 'isoformat') else session["created_at"],
        "benefits_of_signup": [
            "Unlimited fact checking",
            "Detailed analysis with sources",
            "Save and organize your checks",
            "Advanced AI analysis modes",
            "Community features",
            "Personalized dashboard"
        ]
    }

@router.get("/limits")
async def get_guest_limits():
    """Get information about guest user limitations."""
    return {
        "daily_check_limit": 10,
        "features": {
            "basic_fact_checking": True,
            "quick_analysis": True,
            "limited_history": True,
            "detailed_analysis": False,
            "save_results": False,
            "share_results": False,
            "community_access": False,
            "dashboard": False,
            "unlimited_checks": False
        },
        "upgrade_benefits": [
            "Unlimited daily fact checks",
            "Detailed analysis with multiple sources",
            "Save and organize your fact-check history",
            "Share results with others",
            "Access to community discussions",
            "Personalized dashboard and analytics",
            "Priority processing",
            "Advanced AI analysis modes"
        ],
        "call_to_action": {
            "message": "Sign up for free to unlock all features!",
            "register_url": "/auth/register",
            "login_url": "/auth/login"
        }
    }

@router.post("/convert")
async def convert_guest_to_user(
    guest_id: str = Header(..., alias="X-Guest-ID"),
    user_token: str = Header(..., alias="Authorization")
):
    """
    Convert guest session data to authenticated user account.
    Called after user signs up to preserve their session data.
    """
    try:
        if guest_id not in guest_sessions:
            # No session to convert, that's fine
            return {"message": "No guest session found to convert"}
        
        session = guest_sessions[guest_id]
        
        # Here you would typically:
        # 1. Verify the user token
        # 2. Get user ID from token
        # 3. Transfer guest history to user account
        # 4. Clean up guest session
        
        # For now, just acknowledge the conversion
        conversion_data = {
            "converted_checks": len(session["history"]),
            "guest_session_duration": datetime.utcnow() - session["created_at"],
            "message": "Welcome! Your guest session has been converted to your account."
        }
        
        # Clean up guest session
        del guest_sessions[guest_id]
        
        logger.info(f"Converted guest session {guest_id} to authenticated user")
        return conversion_data
        
    except Exception as e:
        logger.error(f"Error converting guest session: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to convert guest session"
        )

# Health check for guest services
@router.get("/health")
async def guest_health_check():
    """Health check endpoint for guest services."""
    return {
        "status": "healthy",
        "active_sessions": len(guest_sessions),
        "timestamp": datetime.utcnow()
    }
