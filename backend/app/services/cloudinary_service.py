"""
Cloudinary service for managing file uploads and storage.
"""
import os
import logging
import cloudinary
import cloudinary.uploader
import cloudinary.api
from typing import Dict, Any, Optional, List, Union
from fastapi import UploadFile, HTTPException
import uuid
from app.core.config import settings

logger = logging.getLogger(__name__)

class CloudinaryService:
    """Service to handle file uploads and storage in Cloudinary."""
    
    def __init__(self):
        """Initialize Cloudinary service with configuration."""
        self.is_initialized = False
        self.config = {
            "cloud_name": settings.CLOUDINARY_CLOUD_NAME,
            "api_key": settings.CLOUDINARY_API_KEY,
            "api_secret": settings.CLOUDINARY_API_SECRET,
            "secure": True
        }
        self._initialize()
    
    def _initialize(self):
        """Initialize Cloudinary SDK."""
        try:
            if all(self.config.values()):
                cloudinary.config(**self.config)
                self.is_initialized = True
                logger.info("✅ Cloudinary service initialized successfully")
            else:
                logger.warning("⚠️ Cloudinary credentials not found. Using mock storage.")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Cloudinary: {str(e)}")
    
    async def upload_file(self, file: UploadFile, folder: str = "general", 
                          resource_type: str = "auto", transformation: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Upload a file to Cloudinary.
        
        Args:
            file: UploadFile object containing the file to upload
            folder: Destination folder in Cloudinary
            resource_type: Type of resource (auto, image, video, raw)
            transformation: Optional transformation to apply during upload
            
        Returns:
            Dictionary containing upload response including URL
        """
        if not self.is_initialized:
            return self._mock_upload_response(file.filename, folder)
        
        try:
            # Validate file size (10MB limit)
            max_size = 10 * 1024 * 1024  # 10MB
            file_size = 0
            
            # Read file content
            contents = await file.read()
            file_size = len(contents)
            
            if file_size > max_size:
                raise HTTPException(
                    status_code=413, 
                    detail=f"File too large. Maximum size is {max_size // (1024 * 1024)}MB"
                )
            
            # Create a unique filename
            file_ext = os.path.splitext(file.filename)[1] if file.filename else ""
            unique_filename = f"{uuid.uuid4().hex}{file_ext}"
            
            # Prepare upload options
            upload_options = {
                "folder": folder,
                "public_id": os.path.splitext(unique_filename)[0],
                "resource_type": resource_type,
                "overwrite": True,
                "unique_filename": False,
                "use_filename": True
            }
            
            # Add transformation if provided
            if transformation:
                upload_options["transformation"] = transformation
            
            # Upload to cloudinary
            response = cloudinary.uploader.upload(contents, **upload_options)
            
            # Reset file pointer for potential future reads
            await file.seek(0)
            
            logger.info(f"✅ File uploaded successfully to Cloudinary: {response['public_id']}")
            return {
                "success": True,
                "url": response["secure_url"],
                "public_id": response["public_id"],
                "resource_type": response["resource_type"],
                "format": response["format"],
                "width": response.get("width"),
                "height": response.get("height"),
                "bytes": response["bytes"],
                "created_at": response["created_at"],
                "version": response["version"]
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"❌ Failed to upload file to Cloudinary: {str(e)}")
            # Fallback to mock response in case of error
            return self._mock_upload_response(file.filename, folder)
    
    async def upload_image(self, file: UploadFile, folder: str = "images",
                          optimize: bool = True) -> Dict[str, Any]:
        """
        Upload an image with optimization.
        
        Args:
            file: UploadFile object containing the image
            folder: Destination folder in Cloudinary
            optimize: Whether to apply optimization transformations
            
        Returns:
            Dictionary containing upload response
        """
        transformation = None
        if optimize:
            transformation = [
                {"quality": "auto"},
                {"format": "auto"},
                {"width": 1200, "height": 1200, "crop": "limit"}
            ]
        
        return await self.upload_file(file, f"misinfoguard/{folder}", "image", transformation)
    
    async def upload_document(self, file: UploadFile, folder: str = "documents") -> Dict[str, Any]:
        """Upload a document file."""
        return await self.upload_file(file, f"misinfoguard/{folder}", "raw")
    
    async def upload_profile_picture(self, file: UploadFile, user_id: str) -> Dict[str, Any]:
        """Upload a user's profile picture with specific transformations."""
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
        """Upload an attachment for a report."""
        return await self.upload_file(file, f"misinfoguard/reports/{report_id}", "auto")
    
    async def delete_file(self, public_id: str, resource_type: str = "image") -> Dict[str, Any]:
        """
        Delete a file from Cloudinary.
        
        Args:
            public_id: Public ID of the resource to delete
            resource_type: Type of the resource (image, video, raw)
            
        Returns:
            Dictionary containing deletion status
        """
        if not self.is_initialized:
            return {"success": True, "message": "Mock deletion successful"}
        
        try:
            response = cloudinary.uploader.destroy(public_id, resource_type=resource_type)
            logger.info(f"✅ File deleted from Cloudinary: {public_id}")
            return {
                "success": response["result"] == "ok",
                "message": f"Deletion {'successful' if response['result'] == 'ok' else 'failed'}",
                "result": response["result"]
            }
        except Exception as e:
            logger.error(f"❌ Failed to delete file from Cloudinary: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def get_resource(self, public_id: str, resource_type: str = "image") -> Dict[str, Any]:
        """Get resource information from Cloudinary."""
        if not self.is_initialized:
            return self._mock_resource_info(public_id)
        
        try:
            response = cloudinary.api.resource(public_id, resource_type=resource_type)
            return {
                "success": True,
                "data": response
            }
        except Exception as e:
            logger.error(f"❌ Failed to get resource info from Cloudinary: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def get_upload_signature(self, folder: str = "general") -> Dict[str, Any]:
        """
        Generate upload signature for client-side uploads.
        
        Args:
            folder: Destination folder
            
        Returns:
            Dictionary containing signature and upload parameters
        """
        if not self.is_initialized:
            return {
                "success": True,
                "signature": "mock_signature",
                "timestamp": 1625097600,
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
                "upload_preset": "unsigned_preset"  # You'll need to create this in Cloudinary
            }
            
            signature = cloudinary.utils.api_sign_request(params, settings.CLOUDINARY_API_SECRET)
            
            return {
                "success": True,
                "signature": signature,
                "timestamp": timestamp,
                "api_key": settings.CLOUDINARY_API_KEY,
                "folder": f"misinfoguard/{folder}",
                "cloud_name": settings.CLOUDINARY_CLOUD_NAME
            }
        except Exception as e:
            logger.error(f"❌ Failed to generate upload signature: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def generate_url(self, public_id: str, transformation: Optional[Dict] = None) -> str:
        """
        Generate URL for a Cloudinary resource.
        
        Args:
            public_id: Public ID of the resource
            transformation: Optional transformation parameters
            
        Returns:
            Generated URL string
        """
        if not self.is_initialized:
            return f"https://mockcloud.example.com/{public_id}.jpg"
        
        try:
            if transformation:
                return cloudinary.CloudinaryImage(public_id).build_url(**transformation)
            else:
                return cloudinary.CloudinaryImage(public_id).build_url()
        except Exception as e:
            logger.error(f"❌ Failed to generate URL: {str(e)}")
            return f"https://mockcloud.example.com/{public_id}.jpg"
    
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
    
    def _mock_resource_info(self, public_id: str) -> Dict[str, Any]:
        """Generate mock resource info for development/testing."""
        return {
            "success": True,
            "data": {
                "public_id": public_id,
                "format": "jpg",
                "resource_type": "image",
                "created_at": "2025-09-10T00:00:00Z",
                "bytes": 12345,
                "width": 800,
                "height": 600,
                "url": f"https://res.cloudinary.com/demo/image/upload/{public_id}.jpg",
                "secure_url": f"https://res.cloudinary.com/demo/image/upload/{public_id}.jpg",
                "version": 1234567890,
                "is_mock": True
            }
        }

# Create a singleton instance
cloudinary_service = CloudinaryService()
