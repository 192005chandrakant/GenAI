"""
User reporting endpoints for flagging content.
"""
import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends
from app.models.dto import BaseResponse
from app.auth.firebase import get_current_user
from app.services.firestore_service import firestore_service
from app.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/{content_id}")
async def report_content(
    content_id: str,
    reason: str,
    description: Optional[str] = None,
    current_user: Optional[dict] = Depends(get_current_user)
):
    """Report content for review."""
    try:
        if settings.use_mocks:
            return BaseResponse(
                success=True,
                message=f"Mock: Reported content {content_id}"
            )
        
        # Store report
        report_id = await firestore_service.create_content_report(
            content_id=content_id,
            reported_by=current_user.get("uid") if current_user else "anonymous",
            reason=reason,
            description=description
        )
        
        return BaseResponse(
            success=True,
            message=f"Content reported successfully: {report_id}"
        )
        
    except Exception as e:
        logger.error(f"Error reporting content: {e}")
        raise HTTPException(status_code=500, detail="Failed to report content")


@router.get("/my-reports")
async def get_my_reports(
    current_user: dict = Depends(get_current_user)
):
    """Get current user's reports."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    try:
        if settings.use_mocks:
            return {"reports": [], "message": "No reports found"}
        
        reports = await firestore_service.get_user_reports(current_user["uid"])
        return {"reports": reports}
        
    except Exception as e:
        logger.error(f"Error getting user reports: {e}")
        raise HTTPException(status_code=500, detail="Failed to get reports")
