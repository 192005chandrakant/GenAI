#!/usr/bin/env python3
"""
Test script to verify Cloudinary integration
"""
import sys
import os
import asyncio
from io import BytesIO
from PIL import Image

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(__file__))

from app.core.config import settings
from app.services.cloudinary_service import CloudinaryService
from app.services.media_service import MediaService

async def test_cloudinary_integration():
    """Test the Cloudinary integration"""
    print("🧪 Testing Cloudinary Integration")
    print("=" * 50)
    
    # Check configuration
    print("📋 Configuration:")
    print(f"Cloud Name: {settings.CLOUDINARY_CLOUD_NAME}")
    print(f"API Key: {settings.CLOUDINARY_API_KEY[:10] + '...' if settings.CLOUDINARY_API_KEY else 'Not set'}")
    print(f"API Secret: {'Set' if settings.CLOUDINARY_API_SECRET else 'Not set'}")
    print()
    
    if not all([settings.CLOUDINARY_CLOUD_NAME, settings.CLOUDINARY_API_KEY, settings.CLOUDINARY_API_SECRET]):
        print("❌ Cloudinary credentials not properly configured in .env file")
        print("Please update the following in your .env file:")
        print("CLOUDINARY_CLOUD_NAME=your_actual_cloud_name")
        print("CLOUDINARY_API_KEY=your_actual_api_key") 
        print("CLOUDINARY_API_SECRET=your_actual_api_secret")
        return False
    
    try:
        # Test CloudinaryService
        print("🔧 Testing CloudinaryService...")
        cloudinary_service = CloudinaryService()
        
        # Create a test image
        test_image = Image.new('RGB', (100, 100), color='red')
        image_buffer = BytesIO()
        test_image.save(image_buffer, format='PNG')
        image_buffer.seek(0)
        
        # Test MediaService 
        print("🔧 Testing MediaService...")
        media_service = MediaService()
        
        print("✅ Services initialized successfully!")
        print()
        print("🎯 To test file upload:")
        print("1. Update your .env file with real Cloudinary credentials")
        print("2. Start both backend (port 8000) and frontend (port 3002)")
        print("3. Visit http://localhost:3002 and try uploading a file")
        
        return True
        
    except Exception as e:
        print(f"❌ Error initializing services: {str(e)}")
        return False

if __name__ == "__main__":
    asyncio.run(test_cloudinary_integration())
