"""
Media upload endpoints for the Misinformation Detection API.
"""
import logging
from typing import List, Optional
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Form, Query
from fastapi.responses import JSONResponse

from app.services.media_service import media_service
from app.auth.firebase import get_current_user
from app.models.dto import User

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/upload/image")
async def upload_image(
    file: UploadFile = File(...),
    optimize: bool = Form(True),
    current_user: dict = Depends(get_current_user)
):
    """
    Upload an image file.
    
    Args:
        file: Image file to upload
        optimize: Whether to apply optimization transformations
        current_user: Current authenticated user
        
    Returns:
        Upload result with URL and metadata
    """
    try:
        user_id = current_user.get("uid", "anonymous")
        result = await media_service.upload_image(file, user_id, optimize)
        
        logger.info(f"Image uploaded successfully for user {user_id}: {result.get('public_id')}")
        return JSONResponse(content=result, status_code=200)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in image upload: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/upload/document")
async def upload_document(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """
    Upload a document file.
    
    Args:
        file: Document file to upload
        current_user: Current authenticated user
        
    Returns:
        Upload result with URL and metadata
    """
    try:
        user_id = current_user.get("uid", "anonymous")
        result = await media_service.upload_document(file, user_id)
        
        logger.info(f"Document uploaded successfully for user {user_id}: {result.get('public_id')}")
        return JSONResponse(content=result, status_code=200)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in document upload: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/upload/profile-picture")
async def upload_profile_picture(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """
    Upload a profile picture for the current user.
    
    Args:
        file: Image file to upload as profile picture
        current_user: Current authenticated user
        
    Returns:
        Upload result with optimized profile picture URL
    """
    try:
        user_id = current_user.get("uid")
        if not user_id:
            raise HTTPException(status_code=401, detail="User ID not found in token")
        
        result = await media_service.upload_profile_picture(file, user_id)
        
        logger.info(f"Profile picture uploaded successfully for user {user_id}")
        return JSONResponse(content=result, status_code=200)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in profile picture upload: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/upload/report-attachment/{report_id}")
async def upload_report_attachment(
    report_id: str,
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """
    Upload an attachment for a specific report.
    
    Args:
        report_id: ID of the report to attach the file to
        file: File to upload as attachment
        current_user: Current authenticated user
        
    Returns:
        Upload result with attachment URL and metadata
    """
    try:
        user_id = current_user.get("uid", "anonymous")
        result = await media_service.upload_report_attachment(file, report_id, user_id)
        
        logger.info(f"Report attachment uploaded for report {report_id} by user {user_id}")
        return JSONResponse(content=result, status_code=200)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in report attachment upload: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/media/{public_id}")
async def delete_media(
    public_id: str,
    resource_type: str = Query("image", description="Type of resource (image, video, raw)"),
    current_user: dict = Depends(get_current_user)
):
    """
    Delete a media file by public ID.
    
    Args:
        public_id: Public ID of the media file to delete
        resource_type: Type of the resource (image, video, raw)
        current_user: Current authenticated user
        
    Returns:
        Deletion result
    """
    try:
        # TODO: Add permission check to ensure user can delete this media
        result = await media_service.delete_media(public_id, resource_type)
        
        user_id = current_user.get("uid", "anonymous")
        logger.info(f"Media deleted by user {user_id}: {public_id}")
        return JSONResponse(content=result, status_code=200)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in media deletion: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/media/{public_id}")
async def get_media_info(
    public_id: str,
    resource_type: str = Query("image", description="Type of resource (image, video, raw)"),
    current_user: dict = Depends(get_current_user)
):
    """
    Get information about a media file.
    
    Args:
        public_id: Public ID of the media file
        resource_type: Type of the resource (image, video, raw)
        current_user: Current authenticated user
        
    Returns:
        Media file information and metadata
    """
    try:
        result = await media_service.get_media_info(public_id, resource_type)
        return JSONResponse(content=result, status_code=200)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error getting media info: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/ocr/extract-text")
async def extract_text_from_image(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """
    Extract text from an image using OCR.
    
    Args:
        file: Image file to extract text from
        current_user: Current authenticated user
        
    Returns:
        Extracted text and confidence information
    """
    try:
        result = await media_service.extract_text_from_image(file)
        
        user_id = current_user.get("uid", "anonymous")
        logger.info(f"OCR text extraction performed by user {user_id}")
        return JSONResponse(content=result, status_code=200)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in OCR text extraction: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/upload/signature")
async def get_upload_signature(
    folder: str = Query("general", description="Destination folder for upload"),
    current_user: dict = Depends(get_current_user)
):
    """
    Get upload signature for client-side uploads.
    
    Args:
        folder: Destination folder for the upload
        current_user: Current authenticated user
        
    Returns:
        Upload signature and parameters for client-side upload
    """
    try:
        result = await media_service.generate_upload_signature(folder)
        return JSONResponse(content=result, status_code=200)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error generating upload signature: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/health")
async def media_health_check():
    """Health check endpoint for media service."""
    try:
        return {
            "status": "healthy",
            "service": "media_upload",
            "cloudinary_available": True,  # This would check actual Cloudinary status
            "supported_formats": {
                "images": ["jpeg", "jpg", "png", "gif", "webp"],
                "documents": ["pdf", "txt", "doc", "docx"],
                "videos": ["mp4", "avi", "mov", "webm"]
            },
            "max_file_size_mb": 10
        }
    except Exception as e:
        logger.error(f"Media service health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }
