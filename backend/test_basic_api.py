#!/usr/bin/env python3
"""
Simple test to check basic API functionality
"""
import requests
import json

def test_basic_api():
    """Test basic API health check first."""
    
    print("🔍 Testing basic API connectivity...")
    
    # Test health endpoint first
    try:
        health_response = requests.get("http://localhost:8000/health", timeout=10)
        print(f"💓 Health check: {health_response.status_code}")
        if health_response.status_code == 200:
            print("✅ Server is responding")
        else:
            print(f"⚠️ Health check failed: {health_response.text}")
            return
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        return
    
    # Test API docs endpoint
    try:
        docs_response = requests.get("http://localhost:8000/api/docs", timeout=10)
        print(f"📚 API docs: {docs_response.status_code}")
    except Exception as e:
        print(f"⚠️ API docs error: {e}")
    
    # Now test the checks endpoint with minimal data
    print("\n🧪 Testing checks endpoint...")
    
    url = "http://localhost:8000/api/v1/checks"
    payload = {
        "inputType": "text",
        "payload": "test",
        "language": "en"
    }
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        print(f"📊 Checks endpoint: {response.status_code}")
        
        if response.status_code != 200:
            print(f"📄 Error response: {response.text}")
            try:
                error_json = response.json()
                print(f"📝 Structured error: {json.dumps(error_json, indent=2)}")
            except:
                pass
        else:
            print("✅ Checks endpoint working!")
            
    except Exception as e:
        print(f"❌ Checks endpoint error: {e}")

if __name__ == "__main__":
    test_basic_api()