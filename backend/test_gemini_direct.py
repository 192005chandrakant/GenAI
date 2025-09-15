#!/usr/bin/env python3
"""
Test just the Gemini service directly.
"""
import sys
import os

# Add the app to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import asyncio
from app.services.gemini_service import gemini_service
from app.core.config import settings

async def test_gemini_service():
    """Test Gemini service directly."""
    print("🤖 Testing Gemini Service Directly")
    print("=" * 40)
    
    # Test content
    test_content = "The earth is flat and NASA is hiding evidence"
    
    print(f"📝 Test content: {test_content}")
    print(f"🔑 API Key configured: {'Yes' if settings.GEMINI_API_KEY else 'No'}")
    print(f"🎯 Model: {settings.GEMINI_MODEL}")
    
    try:
        # Test the fact check fallback directly
        print("\n🔄 Calling fact_check_fallback...")
        
        result = await gemini_service.fact_check_fallback(
            content=test_content,
            content_type="text",
            context={
                "language": "en",
                "source": "user_input",
                "claims_count": 1,
                "test_mode": True
            }
        )
        
        print(f"✅ Result received!")
        print(f"📊 Success: {result.get('success', False)}")
        
        if result.get('success'):
            print(f"🎯 Verdict: {result.get('verdict', 'N/A')}")
            print(f"📊 Credibility Score: {result.get('credibility_score', 'N/A')}")
            print(f"📝 Summary: {result.get('summary', 'N/A')}")
            print(f"📄 Citations: {len(result.get('citations', []))}")
            
            # Show detailed analysis
            detailed = result.get('detailed_analysis', {})
            if detailed:
                print(f"🔍 Key Findings: {len(detailed.get('key_findings', []))}")
                print(f"⚠️ Red Flags: {len(detailed.get('red_flags', []))}")
                print(f"✅ Supporting Evidence: {len(detailed.get('supporting_evidence', []))}")
        else:
            print(f"❌ Error: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Exception occurred: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_gemini_service())