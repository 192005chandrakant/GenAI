"""
Media Processing Service for image and video analysis.
Handles OCR, EXIF extraction, image hashing, and video processing.
"""

import asyncio
import hashlib
import json
import time
from typing import List, Dict, Any, Optional, Tuple
import logging
from datetime import datetime
from pathlib import Path
import tempfile
import os

import cv2
import numpy as np
from PIL import Image, ImageOps, ImageFilter
import imagehash
import pytesseract
from exiftool import ExifToolHelper
import ffmpeg

from app.core.config import settings
from app.models.schemas import MediaMetadata, ContentType

logger = logging.getLogger(__name__)


class MediaService:
    """Service for media processing and analysis."""
    
    def __init__(self):
        """Initialize Media service."""
        self.tesseract_cmd = settings.TESSERACT_CMD
        self.exiftool_path = settings.EXIFTOOL_PATH
        self.ffmpeg_path = settings.FFMPEG_PATH
        
        # Configure Tesseract
        pytesseract.pytesseract.tesseract_cmd = self.tesseract_cmd
        
        logger.info("Media Service initialized")
    
    async def process_image(self, image_data: bytes, filename: str) -> MediaMetadata:
        """Process image for analysis and metadata extraction."""
        try:
            start_time = time.time()
            
            # Create temporary file for processing
            with tempfile.NamedTemporaryFile(delete=False, suffix=Path(filename).suffix) as temp_file:
                temp_file.write(image_data)
                temp_file_path = temp_file.name
            
            try:
                # Extract basic metadata
                file_size = len(image_data)
                mime_type = self._get_mime_type(filename)
                
                # Load image for processing
                image = Image.open(temp_file_path)
                
                # Extract dimensions
                dimensions = {
                    "width": image.width,
                    "height": image.height
                }
                
                # Extract EXIF data
                exif_data = await self._extract_exif_data(temp_file_path)
                
                # Generate image hash
                image_hash = await self._generate_image_hash(image)
                
                # Extract text using OCR
                ocr_text = await self._extract_text_from_image(image)
                
                processing_time_ms = int((time.time() - start_time) * 1000)
                
                metadata = MediaMetadata(
                    file_size=file_size,
                    mime_type=mime_type,
                    dimensions=dimensions,
                    exif_data=exif_data,
                    image_hash=image_hash,
                    ocr_text=ocr_text
                )
                
                logger.info(f"Image processing completed in {processing_time_ms}ms")
                return metadata
                
            finally:
                # Clean up temporary file
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                    
        except Exception as e:
            logger.error(f"Error processing image: {str(e)}")
            raise
    
    async def process_video(self, video_data: bytes, filename: str) -> MediaMetadata:
        """Process video for analysis and metadata extraction."""
        try:
            start_time = time.time()
            
            # Create temporary file for processing
            with tempfile.NamedTemporaryFile(delete=False, suffix=Path(filename).suffix) as temp_file:
                temp_file.write(video_data)
                temp_file_path = temp_file.name
            
            try:
                # Extract basic metadata
                file_size = len(video_data)
                mime_type = self._get_mime_type(filename)
                
                # Extract video metadata using FFmpeg
                video_info = await self._extract_video_info(temp_file_path)
                
                processing_time_ms = int((time.time() - start_time) * 1000)
                
                metadata = MediaMetadata(
                    file_size=file_size,
                    mime_type=mime_type,
                    dimensions=video_info.get("dimensions"),
                    duration=video_info.get("duration"),
                    exif_data=video_info.get("metadata"),
                    ocr_text=""
                )
                
                logger.info(f"Video processing completed in {processing_time_ms}ms")
                return metadata
                
            finally:
                # Clean up temporary file
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                    
        except Exception as e:
            logger.error(f"Error processing video: {str(e)}")
            raise
    
    async def extract_text_from_image(self, image_data: bytes) -> str:
        """Extract text from image using OCR."""
        try:
            # Convert bytes to PIL Image
            image = Image.open(io.BytesIO(image_data))
            
            # Preprocess image for better OCR
            processed_image = await self._preprocess_image_for_ocr(image)
            
            # Extract text
            text = pytesseract.image_to_string(processed_image)
            
            return text.strip()
            
        except Exception as e:
            logger.error(f"Error extracting text from image: {str(e)}")
            return ""
    
    async def generate_image_hash(self, image_data: bytes) -> str:
        """Generate perceptual hash for image."""
        try:
            image = Image.open(io.BytesIO(image_data))
            
            # Generate multiple hash types for better comparison
            hash_average = imagehash.average_hash(image)
            hash_phash = imagehash.phash(image)
            hash_dhash = imagehash.dhash(image)
            hash_whash = imagehash.whash(image)
            
            # Combine hashes
            combined_hash = f"{hash_average}_{hash_phash}_{hash_dhash}_{hash_whash}"
            
            return combined_hash
            
        except Exception as e:
            logger.error(f"Error generating image hash: {str(e)}")
            return ""
    
    # Private helper methods
    
    async def _extract_exif_data(self, file_path: str) -> Dict[str, Any]:
        """Extract EXIF data from file."""
        try:
            with ExifToolHelper() as et:
                metadata = et.get_metadata(file_path)
                if metadata:
                    return metadata[0]
                return {}
        except Exception as e:
            logger.error(f"Error extracting EXIF data: {str(e)}")
            return {}
    
    async def _generate_image_hash(self, image: Image.Image) -> str:
        """Generate perceptual hash for image."""
        try:
            # Generate multiple hash types
            hash_average = imagehash.average_hash(image)
            hash_phash = imagehash.phash(image)
            hash_dhash = imagehash.dhash(image)
            hash_whash = imagehash.whash(image)
            
            # Combine hashes
            combined_hash = f"{hash_average}_{hash_phash}_{hash_dhash}_{hash_whash}"
            
            return combined_hash
            
        except Exception as e:
            logger.error(f"Error generating image hash: {str(e)}")
            return ""
    
    async def _extract_text_from_image(self, image: Image.Image) -> str:
        """Extract text from image using OCR."""
        try:
            # Preprocess image for better OCR
            processed_image = await self._preprocess_image_for_ocr(image)
            
            # Extract text
            text = pytesseract.image_to_string(processed_image)
            
            return text.strip()
            
        except Exception as e:
            logger.error(f"Error extracting text from image: {str(e)}")
            return ""
    
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
    
    async def _extract_video_info(self, file_path: str) -> Dict[str, Any]:
        """Extract video metadata using FFmpeg."""
        try:
            probe = ffmpeg.probe(file_path)
            
            video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
            
            info = {
                "duration": float(probe['format']['duration']) if 'duration' in probe['format'] else None,
                "dimensions": {
                    "width": int(video_stream['width']) if video_stream else None,
                    "height": int(video_stream['height']) if video_stream else None
                },
                "metadata": probe['format'].get('tags', {})
            }
            
            return info
            
        except Exception as e:
            logger.error(f"Error extracting video info: {str(e)}")
            return {}
    
    def _get_mime_type(self, filename: str) -> str:
        """Get MIME type from filename."""
        ext = Path(filename).suffix.lower()
        mime_types = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".gif": "image/gif",
            ".bmp": "image/bmp",
            ".mp4": "video/mp4",
            ".avi": "video/x-msvideo",
            ".mov": "video/quicktime",
            ".webm": "video/webm"
        }
        return mime_types.get(ext, "application/octet-stream")
