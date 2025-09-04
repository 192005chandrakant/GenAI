"""
File upload endpoints for media processing.
"""
import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from app.models.dto import UploadRequest, UploadResponse, BaseResponse
from app.services.firestore_service import firestore_service
from app.core.config import settings
from datetime import datetime, timedelta
import uuid

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/signed-url", response_model=UploadResponse)
async def get_signed_upload_url(request: UploadRequest):
    """
    Get signed URL for direct upload to Cloud Storage.
    """
    try:
        if settings.use_mocks:
            return UploadResponse(
                upload_url="https://mock-bucket.storage.googleapis.com/mock-upload-url",
                file_id=f"file_{uuid.uuid4().hex[:12]}",
                expires_at=datetime.utcnow() + timedelta(hours=1)
            )
        
        # Validate file type
        allowed_types = ["image/jpeg", "image/png", "image/gif", "video/mp4"]
        if request.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"File type {request.content_type} not allowed"
            )
        
        # Generate signed URL (implement GCS service)
        file_id = f"upload_{uuid.uuid4().hex}"
        upload_url = await generate_signed_upload_url(file_id, request.content_type)
        
        return UploadResponse(
            upload_url=upload_url,
            file_id=file_id,
            expires_at=datetime.utcnow() + timedelta(hours=1)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating signed URL: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate upload URL")


@router.post("/direct", response_model=BaseResponse)
async def upload_file_direct(
    file: UploadFile = File(...),
    description: Optional[str] = Form(None)
):
    """
    Direct file upload (for smaller files).
    """
    try:
        # Validate file size
        if hasattr(file, 'size') and file.size > settings.max_file_size:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size: {settings.max_file_size} bytes"
            )
        
        # Validate file type
        if not file.content_type.startswith(('image/', 'video/')):
            raise HTTPException(
                status_code=400,
                detail="Only image and video files are allowed"
            )
        
        if settings.use_mocks:
            return BaseResponse(
                success=True,
                message=f"Mock: Uploaded {file.filename}"
            )
        
        # Process upload (implement actual upload logic)
        file_content = await file.read()
        file_id = await process_file_upload(file_content, file.filename, file.content_type)
        
        return BaseResponse(
            success=True,
            message=f"File uploaded successfully: {file_id}"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        raise HTTPException(status_code=500, detail="File upload failed")


async def generate_signed_upload_url(file_id: str, content_type: str) -> str:
    """Generate signed URL for Cloud Storage upload."""
    # Placeholder - implement with actual GCS client
    return f"https://mock-bucket.storage.googleapis.com/{file_id}"


async def process_file_upload(content: bytes, filename: str, content_type: str) -> str:
    """Process and store uploaded file."""
    # Placeholder - implement actual file processing
    return f"file_{uuid.uuid4().hex}"
