#!/usr/bin/env python3
"""
Test script for Gemini fallback functionality.
"""
import requests
import json
import time

def test_gemini_fallback():
    """Test the Gemini fallback system."""
    
    # API endpoint
    url = "http://localhost:8000/api/v1/checks"
    
    # Test payload
    payload = {
        "inputType": "text",
        "payload": "The earth is flat and NASA is hiding evidence",
        "language": "auto"
    }
    
    # Headers
    headers = {
        "Content-Type": "application/json"
    }
    
    print("🧪 Testing Gemini Fallback System")
    print(f"📤 Sending request to: {url}")
    print(f"📋 Payload: {json.dumps(payload, indent=2)}")
    
    try:
        # Send request
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        print(f"\n📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Request successful!")
            print(f"📝 Verdict: {data.get('verdict', 'N/A')}")
            print(f"🎯 Score: {data.get('score', 'N/A')}")
            print(f"🏷️ Badge: {data.get('badge', 'N/A')}")
            
            # Check for AI analysis citations
            citations = data.get('citations', [])
            ai_citations = [c for c in citations if c.get('category') == 'ai_analysis']
            
            if ai_citations:
                print(f"🤖 Gemini fallback worked! Found {len(ai_citations)} AI analysis citation(s)")
                for citation in ai_citations:
                    print(f"   📄 {citation.get('title', 'N/A')}")
                    print(f"   🔗 {citation.get('url', 'N/A')}")
                    print(f"   📊 Trust Score: {citation.get('trustScore', 'N/A')}")
            else:
                print("⚠️ No AI analysis citations found - check if fallback triggered")
                
            print(f"\n📄 Total citations: {len(citations)}")
            for i, citation in enumerate(citations, 1):
                print(f"   {i}. {citation.get('title', 'N/A')} (category: {citation.get('category', 'N/A')})")
                
        elif response.status_code == 422:
            print("❌ Validation error (422)")
            try:
                error_data = response.json()
                print(f"📄 Error details: {json.dumps(error_data, indent=2)}")
            except:
                print(f"📄 Raw response: {response.text}")
        else:
            print(f"❌ Request failed with status {response.status_code}")
            print(f"📄 Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - make sure backend server is running on http://localhost:8000")
    except requests.exceptions.Timeout:
        print("❌ Request timeout - server took too long to respond")
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")

if __name__ == "__main__":
    test_gemini_fallback()