"""
Media Processing and Storage Service for the Misinformation Detection Platform.
Handles file uploads, image processing, OCR, and integrates with Cloudinary for storage.
"""

import asyncio
import hashlib
import json
import time
import io
from typing import List, Dict, Any, Optional, Tuple
import logging
from datetime import datetime
from pathlib import Path
import tempfile
import os

import cv2
import numpy as np
from PIL import Image, ImageOps, ImageFilter
from fastapi import UploadFile, HTTPException

from app.core.config import settings
from app.services.cloudinary_service import cloudinary_service

logger = logging.getLogger(__name__)


class MediaService:
    """Service for media processing, storage, and analysis."""
    
    def __init__(self):
        """Initialize Media service."""
        self.max_file_size = 10 * 1024 * 1024  # 10MB
        self.allowed_image_types = {"image/jpeg", "image/jpg", "image/png", "image/gif", "image/webp"}
        self.allowed_video_types = {"video/mp4", "video/avi", "video/mov", "video/webm"}
        self.allowed_document_types = {"application/pdf", "text/plain", "application/msword", 
                                     "application/vnd.openxmlformats-officedocument.wordprocessingml.document"}
        
        logger.info("Media Service initialized with Cloudinary storage")
    
    async def upload_image(self, file: UploadFile, user_id: Optional[str] = None, 
                          optimize: bool = True) -> Dict[str, Any]:
        """
        Upload an image file with validation and processing.
        
        Args:
            file: UploadFile object containing the image
            user_id: Optional user ID for folder organization
            optimize: Whether to apply optimization transformations
            
        Returns:
            Dictionary with upload result and metadata
        """
        try:
            # Validate file type
            if not file.content_type or file.content_type not in self.allowed_image_types:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Invalid file type. Allowed types: {', '.join(self.allowed_image_types)}"
                )
            
            # Validate file size
            await self._validate_file_size(file)
            
            # Determine folder structure
            folder = f"images/{user_id}" if user_id else "images/general"
            
            # Upload to Cloudinary
            result = await cloudinary_service.upload_image(file, folder, optimize)
            
            if not result.get("success"):
                raise HTTPException(status_code=500, detail="Failed to upload image")
            
            # Extract additional metadata if needed
            metadata = await self._extract_image_metadata(file)
            
            # Combine upload result with metadata
            return {
                **result,
                "metadata": metadata,
                "file_type": "image",
                "original_filename": file.filename
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error uploading image: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal server error during image upload")
    
    async def upload_document(self, file: UploadFile, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Upload a document file."""
        try:
            # Validate file type
            if not file.content_type or file.content_type not in self.allowed_document_types:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Invalid file type. Allowed types: {', '.join(self.allowed_document_types)}"
                )
            
            # Validate file size
            await self._validate_file_size(file)
            
            # Determine folder structure
            folder = f"documents/{user_id}" if user_id else "documents/general"
            
            # Upload to Cloudinary
            result = await cloudinary_service.upload_document(file, folder)
            
            if not result.get("success"):
                raise HTTPException(status_code=500, detail="Failed to upload document")
            
            return {
                **result,
                "file_type": "document",
                "original_filename": file.filename
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error uploading document: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal server error during document upload")
    
    async def upload_profile_picture(self, file: UploadFile, user_id: str) -> Dict[str, Any]:
        """Upload a user's profile picture with specific transformations."""
        try:
            # Validate file type
            if not file.content_type or file.content_type not in self.allowed_image_types:
                raise HTTPException(
                    status_code=400, 
                    detail="Profile picture must be an image (JPEG, PNG, GIF, or WebP)"
                )
            
            # Validate file size
            await self._validate_file_size(file)
            
            # Upload to Cloudinary with profile-specific transformations
            result = await cloudinary_service.upload_profile_picture(file, user_id)
            
            if not result.get("success"):
                raise HTTPException(status_code=500, detail="Failed to upload profile picture")
            
            return {
                **result,
                "file_type": "profile_image",
                "original_filename": file.filename
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error uploading profile picture: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal server error during profile upload")
    
    async def upload_report_attachment(self, file: UploadFile, report_id: str, 
                                     user_id: Optional[str] = None) -> Dict[str, Any]:
        """Upload an attachment for a report."""
        try:
            # Validate file type (allow images, documents, and videos)
            all_allowed_types = self.allowed_image_types | self.allowed_document_types | self.allowed_video_types
            
            if not file.content_type or file.content_type not in all_allowed_types:
                raise HTTPException(
                    status_code=400, 
                    detail="Invalid file type for report attachment"
                )
            
            # Validate file size
            await self._validate_file_size(file)
            
            # Upload to Cloudinary
            result = await cloudinary_service.upload_report_attachment(file, report_id)
            
            if not result.get("success"):
                raise HTTPException(status_code=500, detail="Failed to upload report attachment")
            
            # Determine file type category
            file_type = "image" if file.content_type in self.allowed_image_types else \
                       "video" if file.content_type in self.allowed_video_types else "document"
            
            return {
                **result,
                "file_type": file_type,
                "report_id": report_id,
                "user_id": user_id,
                "original_filename": file.filename
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error uploading report attachment: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal server error during attachment upload")
    
    async def delete_media(self, public_id: str, resource_type: str = "image") -> Dict[str, Any]:
        """Delete a media file from Cloudinary."""
        try:
            result = await cloudinary_service.delete_file(public_id, resource_type)
            
            if not result.get("success"):
                raise HTTPException(status_code=500, detail="Failed to delete media file")
            
            return result
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error deleting media: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal server error during media deletion")
    
    async def get_media_info(self, public_id: str, resource_type: str = "image") -> Dict[str, Any]:
        """Get information about a media file."""
        try:
            result = await cloudinary_service.get_resource(public_id, resource_type)
            
            if not result.get("success"):
                raise HTTPException(status_code=404, detail="Media file not found")
            
            return result
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting media info: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal server error")
    
    async def extract_text_from_image(self, file: UploadFile) -> Dict[str, Any]:
        """Extract text from an image using OCR."""
        try:
            # Validate file type
            if not file.content_type or file.content_type not in self.allowed_image_types:
                raise HTTPException(status_code=400, detail="File must be an image")
            
            # Read file content
            content = await file.read()
            await file.seek(0)  # Reset file pointer
            
            # Process image for OCR
            image = Image.open(io.BytesIO(content))
            
            # Preprocess for better OCR
            processed_image = await self._preprocess_image_for_ocr(image)
            
            # Extract text
            extracted_text = ""
            if settings.use_mocks:
                # Mock OCR for development
                extracted_text = "This is mock extracted text from the image for development purposes."
            else:
                try:
                    import pytesseract
                    extracted_text = pytesseract.image_to_string(processed_image)
                except ImportError:
                    logger.warning("Tesseract not available, using mock text extraction")
                    extracted_text = "Mock extracted text (Tesseract not installed)"
            
            return {
                "success": True,
                "extracted_text": extracted_text.strip(),
                "confidence": 0.85,  # Mock confidence score
                "language": "en"
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error extracting text from image: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "extracted_text": ""
            }
    
    async def generate_upload_signature(self, folder: str = "general") -> Dict[str, Any]:
        """Generate upload signature for client-side uploads."""
        try:
            result = await cloudinary_service.get_upload_signature(folder)
            return result
            
        except Exception as e:
            logger.error(f"Error generating upload signature: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to generate upload signature")
    
    def generate_image_url(self, public_id: str, transformation: Optional[Dict] = None) -> str:
        """Generate optimized URL for an image."""
        return cloudinary_service.generate_url(public_id, transformation)
    
    # Private helper methods
    
    async def _validate_file_size(self, file: UploadFile):
        """Validate file size."""
        # Read file to check size
        content = await file.read()
        file_size = len(content)
        
        # Reset file pointer
        await file.seek(0)
        
        if file_size > self.max_file_size:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size is {self.max_file_size // (1024 * 1024)}MB"
            )
    
    async def _extract_image_metadata(self, file: UploadFile) -> Dict[str, Any]:
        """Extract basic metadata from an image file."""
        try:
            content = await file.read()
            await file.seek(0)  # Reset file pointer
            
            image = Image.open(io.BytesIO(content))
            
            metadata = {
                "dimensions": {
                    "width": image.width,
                    "height": image.height
                },
                "format": image.format,
                "mode": image.mode,
                "file_size": len(content)
            }
            
            # Try to extract EXIF data
            try:
                exif = image._getexif()
                if exif:
                    metadata["exif"] = {k: v for k, v in exif.items() if isinstance(k, int)}
            except:
                metadata["exif"] = {}
            
            return metadata
            
        except Exception as e:
            logger.error(f"Error extracting image metadata: {str(e)}")
            return {}
    
    async def _preprocess_image_for_ocr(self, image: Image.Image) -> Image.Image:
        """Preprocess image for better OCR results."""
        try:
            # Convert to grayscale
            if image.mode != 'L':
                image = image.convert('L')
            
            # Resize if too small
            if image.width < 100 or image.height < 100:
                image = image.resize((image.width * 2, image.height * 2), Image.LANCZOS)
            
            # Enhance contrast
            image = ImageOps.autocontrast(image)
            
            return image
            
        except Exception as e:
            logger.error(f"Error preprocessing image: {str(e)}")
            return image


# Create a singleton instance
media_service = MediaService()
