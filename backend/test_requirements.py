#!/usr/bin/env python3
"""
Test script to validate requirements.txt dependencies.
This script imports all critical modules to ensure they work correctly.
"""

def test_requirements():
    """Test critical imports to validate requirements.txt"""
    print("Testing requirements.txt dependencies...")
    
    try:
        # Core FastAPI
        import fastapi
        import uvicorn
        print("✓ FastAPI and Uvicorn imported successfully")
        
        # Google Cloud
        from google.cloud import firestore
        from google.cloud import storage
        import google.generativeai as genai
        print("✓ Google Cloud services imported successfully")
        
        # Firebase
        import firebase_admin
        print("✓ Firebase Admin imported successfully")
        
        # Data validation
        import pydantic
        from pydantic_settings import BaseSettings
        print("✓ Pydantic imported successfully")
        
        # AI/ML
        import numpy
        import pandas
        import faiss
        print("✓ ML libraries imported successfully")
        
        # Image processing
        import cv2
        from PIL import Image
        print("✓ Image processing libraries imported successfully")
        
        # Web scraping
        import requests
        import beautifulsoup4
        print("✓ Web scraping libraries imported successfully")
        
        # Auth & Security
        import jwt
        from passlib.context import CryptContext
        print("✓ Auth libraries imported successfully")
        
        print("\n🎉 All requirements.txt dependencies validated successfully!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_app_imports():
    """Test application-specific imports"""
    print("\nTesting application imports...")
    
    try:
        from app.core.config import settings
        print("✓ Settings imported successfully")
        
        from app.models.schemas import UserResponse, CheckResponse
        print("✓ Schemas imported successfully")
        
        # Test if we can create the FastAPI app without errors
        import main
        print("✓ Main application module imported successfully")
        
        print("\n🎉 All application imports validated successfully!")
        return True
        
    except ImportError as e:
        print(f"❌ Application import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected application error: {e}")
        return False

if __name__ == "__main__":
    print("=== Requirements.txt Validation Test ===\n")
    
    requirements_ok = test_requirements()
    app_ok = test_app_imports()
    
    if requirements_ok and app_ok:
        print("\n✅ ALL TESTS PASSED - requirements.txt is stable and working!")
        exit(0)
    else:
        print("\n❌ SOME TESTS FAILED - requirements.txt needs fixes")
        exit(1)
