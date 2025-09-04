"""
Admin endpoints for content moderation and system management.
"""
import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse

from app.models.dto import (
    AdminQueueItem, AllowlistEntry, AllowlistRequest, BaseResponse
)
from app.models.admin_schemas import AnalyticsSummary
from app.models.check_result_schemas import CheckResponse
from app.auth.firebase import require_admin
from app.services.firestore_service import firestore_service
from app.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/queue", response_model=List[AdminQueueItem])
async def get_moderation_queue(
    limit: int = 20,
    priority: Optional[str] = None,
    current_user: dict = Depends(require_admin)
):
    """
    Get content requiring moderation (admin only).
    
    Returns a list of content items flagged for review by the AI system
    or reported by users.
    """
    try:
        if settings.use_mocks:
            # Return mock queue items for development
            return [
                AdminQueueItem(
                    id="queue_001",
                    content="Mock content requiring review",
                    content_type="text",
                    flagged_reason="Suspicious patterns detected",
                    priority="medium",
                    created_at="2025-09-03T10:00:00Z",
                    user_id="user_123"
                )
            ]
        
        queue_items = await firestore_service.get_moderation_queue(
            limit=limit, 
            priority=priority
        )
        return queue_items
        
    except Exception as e:
        logger.error(f"Error getting moderation queue: {e}")
        raise HTTPException(
            status_code=500, 
            detail="Failed to retrieve moderation queue"
        )


@router.post("/moderate/{item_id}")
async def moderate_content(
    item_id: str,
    action: str,  # approve, reject, escalate
    notes: Optional[str] = None,
    current_user: dict = Depends(require_admin)
):
    """
    Take moderation action on a queue item.
    """
    try:
        if action not in ["approve", "reject", "escalate"]:
            raise HTTPException(
                status_code=400,
                detail="Action must be one of: approve, reject, escalate"
            )
        
        if settings.use_mocks:
            return {"success": True, "message": f"Mock: {action} applied to {item_id}"}
        
        result = await firestore_service.moderate_content(
            item_id=item_id,
            action=action,
            moderator_id=current_user["uid"],
            notes=notes
        )
        
        if not result:
            raise HTTPException(status_code=404, detail="Queue item not found")
        
        return {"success": True, "message": f"Content {action}ed successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error moderating content {item_id}: {e}")
        raise HTTPException(status_code=500, detail="Moderation action failed")


@router.get("/allowlist", response_model=List[AllowlistEntry])
async def get_allowlist(
    limit: int = 100,
    category: Optional[str] = None,
    current_user: dict = Depends(require_admin)
):
    """
    Get trusted source allowlist.
    """
    try:
        if settings.use_mocks:
            return [
                AllowlistEntry(
                    domain="reuters.com",
                    trust_score=95,
                    category="news",
                    notes="Established news agency",
                    added_by="admin",
                    added_at="2025-09-01T00:00:00Z"
                ),
                AllowlistEntry(
                    domain="snopes.com",
                    trust_score=90,
                    category="fact_check",
                    notes="Fact-checking website",
                    added_by="admin",
                    added_at="2025-09-01T00:00:00Z"
                )
            ]
        
        allowlist = await firestore_service.get_allowlist(
            limit=limit,
            category=category
        )
        return allowlist
        
    except Exception as e:
        logger.error(f"Error getting allowlist: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve allowlist")


@router.post("/allowlist", response_model=BaseResponse)
async def add_to_allowlist(
    request: AllowlistRequest,
    current_user: dict = Depends(require_admin)
):
    """
    Add domain to trusted sources allowlist.
    """
    try:
        if settings.use_mocks:
            return BaseResponse(
                success=True,
                message=f"Mock: Added {request.domain} to allowlist"
            )
        
        # Validate domain format
        domain = request.domain.lower().strip()
        if not domain or "." not in domain:
            raise HTTPException(
                status_code=400,
                detail="Invalid domain format"
            )
        
        entry = AllowlistEntry(
            domain=domain,
            trust_score=request.trust_score,
            category=request.category,
            notes=request.notes,
            added_by=current_user["uid"]
        )
        
        result = await firestore_service.add_to_allowlist(entry)
        if not result:
            raise HTTPException(
                status_code=409,
                detail="Domain already exists in allowlist"
            )
        
        return BaseResponse(
            success=True,
            message=f"Added {domain} to allowlist successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding to allowlist: {e}")
        raise HTTPException(status_code=500, detail="Failed to add to allowlist")


@router.delete("/allowlist/{domain}")
async def remove_from_allowlist(
    domain: str,
    current_user: dict = Depends(require_admin)
):
    """
    Remove domain from allowlist.
    """
    try:
        if settings.use_mocks:
            return {"success": True, "message": f"Mock: Removed {domain} from allowlist"}
        
        result = await firestore_service.remove_from_allowlist(domain)
        if not result:
            raise HTTPException(status_code=404, detail="Domain not found in allowlist")
        
        return {"success": True, "message": f"Removed {domain} from allowlist"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error removing from allowlist: {e}")
        raise HTTPException(status_code=500, detail="Failed to remove from allowlist")


@router.get("/analytics", response_model=AnalyticsSummary)
async def get_analytics_summary(
    days: int = 7,
    current_user: dict = Depends(require_admin)
):
    """
    Get analytics summary for admin dashboard.
    """
    try:
        if settings.use_mocks:
            return AnalyticsSummary(
                total_checks=1250,
                avg_score=72.5,
                avg_latency_ms=2100,
                verdicts_distribution={
                    "true": 45,
                    "misleading": 30,
                    "needs_context": 20,
                    "false": 5
                },
                languages_distribution={
                    "en": 60,
                    "hi": 25,
                    "bn": 10,
                    "other": 5
                },
                content_types_distribution={
                    "text": 70,
                    "url": 25,
                    "image": 5
                },
                time_period=f"Last {days} days"
            )
        
        analytics = await firestore_service.get_analytics_summary(days)
        return analytics
        
    except Exception as e:
        logger.error(f"Error getting analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve analytics")


@router.get("/checks", response_model=List[CheckResponse])
async def get_admin_checks(
    limit: int = 50,
    filter_type: Optional[str] = None,  # flagged, low_confidence, reported
    current_user: dict = Depends(require_admin)
):
    """
    Get checks for admin review with filtering options.
    """
    try:
        if settings.use_mocks:
            return []  # Return empty list for mocks
        
        checks = await firestore_service.get_admin_checks(
            limit=limit,
            filter_type=filter_type
        )
        return checks
        
    except Exception as e:
        logger.error(f"Error getting admin checks: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve checks")


@router.post("/users/{user_id}/admin")
async def set_user_admin(
    user_id: str,
    is_admin: bool = True,
    current_user: dict = Depends(require_admin)
):
    """
    Set admin privileges for a user.
    """
    try:
        if settings.use_mocks:
            return {"success": True, "message": f"Mock: Set admin={is_admin} for user {user_id}"}
        
        # Use Firebase auth service to set custom claims
        from app.auth.firebase import set_admin_claim
        result = await set_admin_claim(user_id, is_admin)
        
        if not result:
            raise HTTPException(
                status_code=404,
                detail="User not found or failed to update"
            )
        
        # Also update in Firestore
        await firestore_service.update_user_admin_status(user_id, is_admin)
        
        return {
            "success": True, 
            "message": f"User {user_id} admin status set to {is_admin}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error setting admin status: {e}")
        raise HTTPException(status_code=500, detail="Failed to update user admin status")


@router.post("/system/cache/clear")
async def clear_system_cache(
    cache_type: str = "all",  # all, faiss, firestore
    current_user: dict = Depends(require_admin)
):
    """
    Clear system caches.
    """
    try:
        if settings.use_mocks:
            return {"success": True, "message": f"Mock: Cleared {cache_type} cache"}
        
        if cache_type == "all":
            # Clear all caches
            await firestore_service.clear_cache()
            # Clear FAISS cache if implemented
            # await faiss_service.clear_cache()
        elif cache_type == "firestore":
            await firestore_service.clear_cache()
        elif cache_type == "faiss":
            # await faiss_service.clear_cache()
            pass
        else:
            raise HTTPException(
                status_code=400,
                detail="Cache type must be one of: all, faiss, firestore"
            )
        
        return {"success": True, "message": f"Cleared {cache_type} cache"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        raise HTTPException(status_code=500, detail="Failed to clear cache")


@router.get("/system/health")
async def admin_system_health(
    current_user: dict = Depends(require_admin)
):
    """
    Get detailed system health information for admins.
    """
    try:
        if settings.use_mocks:
            return {
                "status": "healthy",
                "services": {
                    "firestore": "connected",
                    "vertex_ai": "connected",
                    "fact_check_api": "connected",
                    "firebase_auth": "connected"
                },
                "metrics": {
                    "total_checks_today": 245,
                    "avg_response_time_ms": 2100,
                    "error_rate_percent": 1.2,
                    "cache_hit_rate_percent": 78.5
                }
            }
        
        health_info = await firestore_service.get_system_health()
        return health_info
        
    except Exception as e:
        logger.error(f"Error getting system health: {e}")
        raise HTTPException(status_code=500, detail="Failed to get system health")


@router.post("/feature-flags/{flag_name}")
async def toggle_feature_flag(
    flag_name: str,
    enabled: bool,
    current_user: dict = Depends(require_admin)
):
    """
    Toggle feature flags for A/B testing and gradual rollouts.
    """
    try:
        if settings.use_mocks:
            return {"success": True, "message": f"Mock: Set {flag_name} = {enabled}"}
        
        valid_flags = [
            "a_b_testing", "advanced_forensics", "multilingual_beta",
            "community_features", "crisis_mode"
        ]
        
        if flag_name not in valid_flags:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid flag name. Valid flags: {valid_flags}"
            )
        
        result = await firestore_service.set_feature_flag(flag_name, enabled)
        return {
            "success": True,
            "message": f"Feature flag {flag_name} set to {enabled}",
            "flag": flag_name,
            "enabled": enabled
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error toggling feature flag: {e}")
        raise HTTPException(status_code=500, detail="Failed to toggle feature flag")
