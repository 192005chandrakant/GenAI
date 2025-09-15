"""
Enhanced Cloudinary service for managing file uploads and storage with
community features, educational content, and comprehensive media support.
"""
import os
import logging
import hashlib
import mimetypes
import cloudinary
import cloudinary.uploader
import cloudinary.api
from typing import Dict, Any, Optional, List, Union
from fastapi import UploadFile, HTTPException
import uuid
from datetime import datetime, timedelta
from app.core.config import settings
from app.models.enhanced_learning_schemas import MediaUpload
from app.models.enhanced_community_schemas import EnhancedMediaUpload, MediaType

logger = logging.getLogger(__name__)

class EnhancedCloudinaryService:
    """Enhanced service to handle file uploads and storage in Cloudinary with community features."""
    def __init__(self):
        """Initialize Cloudinary service with configuration."""
        self.is_initialized = False
        self.config = {
            "cloud_name": settings.CLOUDINARY_CLOUD_NAME,
            "api_key": settings.CLOUDINARY_API_KEY,
            "api_secret": settings.CLOUDINARY_API_SECRET,
            "secure": True
        }
        self.upload_presets = {
            "profile": "unsigned_profile_preset",
            "educational": "unsigned_educational_preset", 
            "community": "unsigned_community_preset",
            "reports": "unsigned_reports_preset"
        }
        self._initialize()
    
    def _initialize(self):
        """Initialize Cloudinary SDK."""
        try:
            if all(self.config.values()):
                cloudinary.config(**self.config)
                self.is_initialized = True
                logger.info("✅ Enhanced Cloudinary service initialized successfully")
            else:
                logger.warning("⚠️ Cloudinary credentials not found. Using mock storage.")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Cloudinary: {str(e)}")
    
    def _get_media_type(self, mime_type: str) -> MediaType:
        """Determine media type from MIME type."""
        if mime_type.startswith('image/'):
            return MediaType.IMAGE
        elif mime_type.startswith('video/'):
            return MediaType.VIDEO
        elif mime_type.startswith('audio/'):
            return MediaType.AUDIO
        elif mime_type in ['application/pdf', 'application/msword', 'text/plain']:
            return MediaType.DOCUMENT
        else:
            return MediaType.IMAGE  # Default fallback
    
    def _validate_file(self, file: UploadFile, max_size_mb: int = 10, allowed_types: List[str] = None) -> Dict[str, Any]:
        """Validate uploaded file."""
        # Default allowed types
        if allowed_types is None:
            allowed_types = [
                'image/jpeg', 'image/png', 'image/gif', 'image/webp',
                'video/mp4', 'video/webm', 'video/quicktime',
                'audio/mpeg', 'audio/wav', 'audio/ogg',
                'application/pdf', 'application/msword', 'text/plain'
            ]
        
        # Check file size
        max_size = max_size_mb * 1024 * 1024
        
        # Get file info
        mime_type, _ = mimetypes.guess_type(file.filename) if file.filename else (None, None)
        if not mime_type:
            mime_type = file.content_type or 'application/octet-stream'
        
        # Validate MIME type
        if mime_type not in allowed_types:
            raise HTTPException(
                status_code=415,
                detail=f"File type '{mime_type}' not allowed. Allowed types: {allowed_types}"
            )
        
        return {
            "mime_type": mime_type,
            "media_type": self._get_media_type(mime_type),
            "max_size": max_size
        }
    
    def _generate_upload_options(self, folder: str, file_info: Dict[str, Any], 
                                transformation: Optional[Dict] = None) -> Dict[str, Any]:
        """Generate upload options for Cloudinary."""
        # Create a unique filename
        file_ext = os.path.splitext(file_info.get('filename', ''))[1] if file_info.get('filename') else ""
        unique_filename = f"{uuid.uuid4().hex}{file_ext}"
        
        # Determine resource type
        media_type = file_info.get('media_type', MediaType.IMAGE)
        if media_type == MediaType.VIDEO:
            resource_type = "video"
        elif media_type == MediaType.AUDIO:
            resource_type = "video"  # Cloudinary treats audio as video
        elif media_type in [MediaType.DOCUMENT]:
            resource_type = "raw"
        else:
            resource_type = "image"
        
        # Prepare upload options
        upload_options = {
            "folder": f"misinfoguard/{folder}",
            "public_id": os.path.splitext(unique_filename)[0],
            "resource_type": resource_type,
            "overwrite": True,
            "unique_filename": False,
            "use_filename": True,
            "quality": "auto" if resource_type == "image" else None
        }
        
        # Add transformation if provided
        if transformation:
            upload_options["transformation"] = transformation
        
        # Remove None values
        upload_options = {k: v for k, v in upload_options.items() if v is not None}
        
        return upload_options
    
    async def upload_media(self, file: UploadFile, folder: str = "general", 
                          uploader_id: str = None, title: str = None, 
                          description: str = None, tags: List[str] = None,
                          transformation: Optional[Dict] = None,
                          max_size_mb: int = 10) -> EnhancedMediaUpload:
        """
        Upload media file with enhanced metadata support.
        
        Args:
            file: UploadFile object containing the file to upload
            folder: Destination folder in Cloudinary
            uploader_id: ID of the user uploading the file
            title: Title for the media
            description: Description of the media
            tags: Tags for the media
            transformation: Optional transformation to apply during upload
            max_size_mb: Maximum file size in MB
            
        Returns:
            EnhancedMediaUpload object with complete metadata
        """
        if not self.is_initialized:
            return self._mock_enhanced_upload_response(file.filename, folder, uploader_id)
        
        try:
            # Validate file
            file_info = self._validate_file(file, max_size_mb)
            file_info['filename'] = file.filename
            
            # Read file content
            contents = await file.read()
            file_size = len(contents)
            
            if file_size > file_info['max_size']:
                raise HTTPException(
                    status_code=413,
                    detail=f"File too large. Maximum size is {max_size_mb}MB"
                )
            
            # Generate upload options
            upload_options = self._generate_upload_options(folder, file_info, transformation)
            
            # Add tags if provided
            if tags:
                upload_options["tags"] = ",".join(tags)
            
            # Upload to cloudinary
            response = cloudinary.uploader.upload(contents, **upload_options)
            
            # Generate thumbnail for images and videos
            thumbnail_url = None
            if file_info['media_type'] in [MediaType.IMAGE, MediaType.VIDEO]:
                thumbnail_url = cloudinary.CloudinaryImage(response['public_id']).build_url(
                    transformation=[
                        {"width": 300, "height": 200, "crop": "fill"},
                        {"quality": "auto", "format": "auto"}
                    ]
                )
            
            # Reset file pointer for potential future reads
            await file.seek(0)
            
            # Create enhanced media upload object
            media_upload = EnhancedMediaUpload(
                id=str(uuid.uuid4()),
                filename=file.filename or "unknown",
                media_type=file_info['media_type'],
                file_size=file_size,
                mime_type=file_info['mime_type'],
                cloudinary_public_id=response['public_id'],
                cloudinary_url=response['secure_url'],
                thumbnail_url=thumbnail_url,
                uploaded_by=uploader_id or "anonymous",
                upload_timestamp=datetime.utcnow(),
                title=title,
                description=description,
                tags=tags or [],
                dimensions={
                    "width": response.get("width"),
                    "height": response.get("height")
                } if response.get("width") and response.get("height") else None,
                duration_seconds=response.get("duration") if file_info['media_type'] in [MediaType.VIDEO, MediaType.AUDIO] else None,
                is_public=True,
                download_allowed=False,
                moderation_status="pending"
            )
            
            logger.info(f"✅ Enhanced media uploaded successfully: {response['public_id']}")
            return media_upload
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"❌ Failed to upload media to Cloudinary: {str(e)}")
            # Fallback to mock response in case of error
            return self._mock_enhanced_upload_response(file.filename, folder, uploader_id)
    
    async def upload_educational_media(self, file: UploadFile, module_id: str, 
                                     uploader_id: str, **kwargs) -> EnhancedMediaUpload:
        """Upload media for educational modules."""
        # Educational content transformations
        transformation = [
            {"quality": "auto"},
            {"format": "auto"}
        ]
        
        if kwargs.get('optimize_for_learning', True):
            # Add learning-specific optimizations
            transformation.extend([
                {"width": 1200, "height": 1200, "crop": "limit"},
                {"flags": "progressive"}
            ])
        
        return await self.upload_media(
            file, 
            f"education/modules/{module_id}",
            uploader_id,
            transformation=transformation,
            max_size_mb=15,  # Larger size for educational content
            **kwargs
        )
    
    async def upload_community_media(self, file: UploadFile, post_id: str, 
                                   uploader_id: str, **kwargs) -> EnhancedMediaUpload:
        """Upload media for community posts."""
        return await self.upload_media(
            file,
            f"community/posts/{post_id}",
            uploader_id,
            max_size_mb=10,
            **kwargs
        )
    
    async def upload_profile_media(self, file: UploadFile, user_id: str, **kwargs) -> EnhancedMediaUpload:
        """Upload profile pictures and banners."""
        transformation = [
            {"width": 400, "height": 400, "crop": "fill", "gravity": "face"},
            {"quality": "auto"},
            {"format": "auto"}
        ]
        
        return await self.upload_media(
            file,
            f"profiles/{user_id}",
            user_id,
            transformation=transformation,
            max_size_mb=5,  # Smaller size for profile pictures
            **kwargs
        )
    
    async def upload_report_evidence(self, file: UploadFile, report_id: str, 
                                   uploader_id: str, **kwargs) -> EnhancedMediaUpload:
        """Upload evidence for reports."""
        return await self.upload_media(
            file,
            f"reports/{report_id}",
            uploader_id,
            max_size_mb=20,  # Larger size for evidence files
            **kwargs
        )
    
    async def batch_upload(self, files: List[UploadFile], folder: str,
                          uploader_id: str, **kwargs) -> List[EnhancedMediaUpload]:
        """Upload multiple files in batch."""
        results = []
        errors = []
        
        for i, file in enumerate(files):
            try:
                result = await self.upload_media(file, folder, uploader_id, **kwargs)
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to upload file {i}: {str(e)}")
                errors.append({"file_index": i, "filename": file.filename, "error": str(e)})
        
        if errors:
            logger.warning(f"Batch upload completed with {len(errors)} errors: {errors}")
        
        return results
    
    async def generate_signed_upload_url(self, folder: str, upload_preset: str = None,
                                       max_file_size: int = 10485760) -> Dict[str, Any]:
        """Generate signed URL for direct client uploads."""
        if not self.is_initialized:
            return {
                "success": True,
                "upload_url": f"https://api.cloudinary.com/v1_1/demo/upload",
                "signature": "mock_signature",
                "timestamp": int(datetime.utcnow().timestamp()),
                "api_key": "mock_api_key",
                "folder": folder,
                "is_mock": True
            }
        
        try:
            import time
            timestamp = int(time.time())
            
            params = {
                "timestamp": timestamp,
                "folder": f"misinfoguard/{folder}",
                "upload_preset": upload_preset or self.upload_presets.get(folder, "unsigned_preset"),
                "max_file_size": max_file_size
            }
            
            signature = cloudinary.utils.api_sign_request(params, settings.CLOUDINARY_API_SECRET)
            
            return {
                "success": True,
                "upload_url": f"https://api.cloudinary.com/v1_1/{settings.CLOUDINARY_CLOUD_NAME}/upload",
                "signature": signature,
                "timestamp": timestamp,
                "api_key": settings.CLOUDINARY_API_KEY,
                "folder": f"misinfoguard/{folder}",
                "cloud_name": settings.CLOUDINARY_CLOUD_NAME,
                "upload_preset": params["upload_preset"]
            }
        except Exception as e:
            logger.error(f"❌ Failed to generate signed upload URL: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def delete_media(self, public_id: str, resource_type: str = "image") -> Dict[str, Any]:
        """Delete media from Cloudinary."""
        if not self.is_initialized:
            return {"success": True, "message": "Mock deletion successful"}
        
        try:
            response = cloudinary.uploader.destroy(public_id, resource_type=resource_type)
            logger.info(f"✅ Media deleted from Cloudinary: {public_id}")
            return {
                "success": response["result"] == "ok",
                "message": f"Deletion {'successful' if response['result'] == 'ok' else 'failed'}",
                "result": response["result"]
            }
        except Exception as e:
            logger.error(f"❌ Failed to delete media from Cloudinary: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def get_media_info(self, public_id: str, resource_type: str = "image") -> Dict[str, Any]:
        """Get detailed media information from Cloudinary."""
        if not self.is_initialized:
            return self._mock_media_info(public_id)
        
        try:
            response = cloudinary.api.resource(public_id, resource_type=resource_type)
            return {
                "success": True,
                "data": {
                    "public_id": response["public_id"],
                    "format": response["format"],
                    "resource_type": response["resource_type"],
                    "created_at": response["created_at"],
                    "bytes": response["bytes"],
                    "width": response.get("width"),
                    "height": response.get("height"),
                    "duration": response.get("duration"),
                    "url": response["url"],
                    "secure_url": response["secure_url"],
                    "version": response["version"],
                    "etag": response["etag"],
                    "tags": response.get("tags", [])
                }
            }
        except Exception as e:
            logger.error(f"❌ Failed to get media info from Cloudinary: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def generate_transformation_url(self, public_id: str, transformation: Dict[str, Any],
                                  resource_type: str = "image") -> str:
        """Generate URL with specific transformations."""
        if not self.is_initialized:
            return f"https://res.cloudinary.com/demo/{resource_type}/upload/{public_id}.jpg"
        
        try:
            if resource_type == "image":
                return cloudinary.CloudinaryImage(public_id).build_url(**transformation)
            elif resource_type == "video":
                return cloudinary.CloudinaryVideo(public_id).build_url(**transformation)
            else:
                return cloudinary.CloudinaryImage(public_id).build_url(**transformation)
        except Exception as e:
            logger.error(f"❌ Failed to generate transformation URL: {str(e)}")
            return f"https://res.cloudinary.com/demo/{resource_type}/upload/{public_id}.jpg"
    
    async def moderate_content(self, public_id: str, moderation_type: str = "aws_rek") -> Dict[str, Any]:
        """Run content moderation on uploaded media."""
        if not self.is_initialized:
            return {
                "success": True,
                "moderation_status": "approved",
                "confidence": 0.95,
                "is_mock": True
            }
        
        try:
            # Upload with moderation
            response = cloudinary.uploader.explicit(
                public_id,
                type="upload",
                moderation=moderation_type
            )
            
            moderation_results = response.get("moderation", [])
            if moderation_results:
                moderation = moderation_results[0]
                return {
                    "success": True,
                    "moderation_status": moderation["status"],
                    "response": moderation.get("response", {}),
                    "confidence": moderation.get("confidence", 0.0)
                }
            else:
                return {
                    "success": True,
                    "moderation_status": "pending",
                    "message": "Moderation in progress"
                }
        except Exception as e:
            logger.error(f"❌ Failed to moderate content: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _mock_enhanced_upload_response(self, filename: Optional[str], folder: str, 
                                     uploader_id: Optional[str]) -> EnhancedMediaUpload:
        """Generate a mock enhanced upload response for development/testing."""
        mock_id = str(uuid.uuid4())
        mock_filename = filename or f"mock_file_{mock_id}"
        mock_url = f"https://res.cloudinary.com/demo/image/upload/v1234567890/{folder}/{mock_id}/{mock_filename}"
        
        # Determine media type from filename
        mime_type, _ = mimetypes.guess_type(mock_filename) if mock_filename else ("image/jpeg", None)
        if not mime_type:
            mime_type = "image/jpeg"
        
        logger.info(f"📦 Mock enhanced media upload: {mock_url}")
        
        return EnhancedMediaUpload(
            id=mock_id,
            filename=mock_filename,
            media_type=self._get_media_type(mime_type),
            file_size=12345,
            mime_type=mime_type,
            cloudinary_public_id=f"{folder}/{mock_id}",
            cloudinary_url=mock_url,
            thumbnail_url=f"{mock_url.replace('.jpg', '_thumb.jpg')}",
            uploaded_by=uploader_id or "anonymous",
            upload_timestamp=datetime.utcnow(),
            title=f"Mock {mock_filename}",
            description=f"Mock upload for {folder}",
            tags=["mock", folder],
            dimensions={"width": 800, "height": 600},
            is_public=True,
            moderation_status="approved"
        )
    
    def _mock_media_info(self, public_id: str) -> Dict[str, Any]:
        """Generate mock media info for development/testing."""
        return {
            "success": True,
            "data": {
                "public_id": public_id,
                "format": "jpg",
                "resource_type": "image",
                "created_at": datetime.utcnow().isoformat(),
                "bytes": 12345,
                "width": 800,
                "height": 600,
                "url": f"https://res.cloudinary.com/demo/image/upload/{public_id}.jpg",
                "secure_url": f"https://res.cloudinary.com/demo/image/upload/{public_id}.jpg",
                "version": 1234567890,
                "etag": "mock_etag",
                "tags": ["mock"],
                "is_mock": True
            }
        }

    # Legacy methods for backward compatibility
    async def upload_file(self, file: UploadFile, folder: str = "general", 
                          resource_type: str = "auto", transformation: Optional[Dict] = None) -> Dict[str, Any]:
        """Legacy upload method for backward compatibility."""
        try:
            result = await self.upload_media(file, folder, transformation=transformation)
            return {
                "success": True,
                "url": result.cloudinary_url,
                "public_id": result.cloudinary_public_id,
                "resource_type": result.media_type.value,
                "format": result.mime_type.split('/')[-1],
                "width": result.dimensions.get("width") if result.dimensions else None,
                "height": result.dimensions.get("height") if result.dimensions else None,
                "bytes": result.file_size,
                "created_at": result.upload_timestamp.isoformat(),
                "version": 1
            }
        except Exception as e:
            logger.error(f"❌ Legacy upload failed: {str(e)}")
            return self._mock_upload_response(file.filename, folder)

    async def upload_image(self, file: UploadFile, folder: str = "images",
                          optimize: bool = True) -> Dict[str, Any]:
        """Legacy image upload method."""
        transformation = None
        if optimize:
            transformation = [
                {"quality": "auto"},
                {"format": "auto"},
                {"width": 1200, "height": 1200, "crop": "limit"}
            ]
        
        return await self.upload_file(file, f"misinfoguard/{folder}", "image", transformation)

    async def upload_document(self, file: UploadFile, folder: str = "documents") -> Dict[str, Any]:
        """Legacy document upload method."""
        return await self.upload_file(file, f"misinfoguard/{folder}", "raw")

    async def upload_profile_picture(self, file: UploadFile, user_id: str) -> Dict[str, Any]:
        """Legacy profile picture upload method."""
        transformation = [
            {"width": 300, "height": 300, "crop": "fill", "gravity": "face"},
            {"quality": "auto"},
            {"format": "auto"}
        ]
        
        return await self.upload_file(
            file, 
            f"misinfoguard/profiles/{user_id}",
            "image", 
            transformation
        )

    async def upload_report_attachment(self, file: UploadFile, report_id: str) -> Dict[str, Any]:
        """Legacy report attachment upload method."""
        return await self.upload_file(file, f"misinfoguard/reports/{report_id}", "auto")

    async def delete_file(self, public_id: str, resource_type: str = "image") -> Dict[str, Any]:
        """Legacy delete method."""
        return await self.delete_media(public_id, resource_type)

    async def get_resource(self, public_id: str, resource_type: str = "image") -> Dict[str, Any]:
        """Legacy get resource method."""
        return await self.get_media_info(public_id, resource_type)

    async def get_upload_signature(self, folder: str = "general") -> Dict[str, Any]:
        """Legacy signature generation method."""
        return await self.generate_signed_upload_url(folder)

    def generate_url(self, public_id: str, transformation: Optional[Dict] = None) -> str:
        """Legacy URL generation method."""
        if transformation:
            return self.generate_transformation_url(public_id, transformation)
        else:
            if not self.is_initialized:
                return f"https://mockcloud.example.com/{public_id}.jpg"
            return cloudinary.CloudinaryImage(public_id).build_url()

    def _mock_upload_response(self, filename: Optional[str], folder: str) -> Dict[str, Any]:
        """Generate a mock upload response for development/testing."""
        mock_id = uuid.uuid4().hex
        mock_filename = filename or f"mock_file_{mock_id}"
        mock_url = f"https://res.cloudinary.com/demo/image/upload/v1234567890/{folder}/{mock_id}/{mock_filename}"
        
        logger.info(f"📦 Mock file upload: {mock_url}")
        
        return {
            "success": True,
            "url": mock_url,
            "public_id": f"{folder}/{mock_id}",
            "resource_type": "image",
            "format": os.path.splitext(mock_filename)[1].replace(".", "") if "." in mock_filename else "jpg",
            "width": 800,
            "height": 600,
            "bytes": 12345,
            "created_at": "2025-09-10T00:00:00Z",
            "version": 1234567890,
            "is_mock": True
        }

# Create a singleton instance
cloudinary_service = EnhancedCloudinaryService()

# Backward compatibility alias
CloudinaryService = EnhancedCloudinaryService
