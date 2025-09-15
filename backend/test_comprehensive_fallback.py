#!/usr/bin/env python3
"""
Comprehensive test for Gemini fallback functionality.
"""
import requests
import json
import time

def test_fallback_scenarios():
    """Test different scenarios for Gemini fallback."""
    
    url = "http://localhost:8000/api/v1/checks"
    headers = {"Content-Type": "application/json"}
    
    scenarios = [
        {
            "name": "Flat Earth Conspiracy",
            "payload": "The earth is flat and NASA is hiding evidence",
            "expected_ai_fallback": True
        },
        {
            "name": "COVID Misinformation",
            "payload": "COVID vaccines contain microchips for tracking",
            "expected_ai_fallback": True
        },
        {
            "name": "Simple Factual Statement",
            "payload": "Water boils at 100 degrees Celsius",
            "expected_ai_fallback": True  # Should still trigger in current mock setup
        }
    ]
    
    print("🧪 Testing Gemini Fallback System - Multiple Scenarios")
    print("=" * 60)
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n📋 Scenario {i}: {scenario['name']}")
        print(f"💬 Content: {scenario['payload']}")
        
        test_payload = {
            "inputType": "text",
            "payload": scenario['payload'],
            "language": "auto"
        }
        
        try:
            start_time = time.time()
            response = requests.post(url, json=test_payload, headers=headers, timeout=30)
            duration = time.time() - start_time
            
            print(f"⏱️ Response time: {duration:.2f}s")
            print(f"📊 Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                # Basic response info
                print(f"✅ Success!")
                print(f"📝 Verdict: {data.get('verdict', 'N/A')}")
                print(f"🎯 Score: {data.get('score', 'N/A')}")
                print(f"🏷️ Badge: {data.get('badge', 'N/A')}")
                
                # Analyze citations
                citations = data.get('citations', [])
                print(f"📄 Total citations: {len(citations)}")
                
                # Check for AI analysis citations
                ai_citations = [c for c in citations if c.get('category') == 'ai_analysis']
                
                if ai_citations:
                    print(f"🤖 AI Fallback Detected: {len(ai_citations)} AI citation(s)")
                    for ai_citation in ai_citations:
                        print(f"   🔍 Title: {ai_citation.get('title', 'N/A')}")
                        print(f"   📊 Trust Score: {ai_citation.get('trustScore', 'N/A')}")
                        print(f"   📝 Excerpt: {ai_citation.get('excerpt', 'N/A')[:100]}...")
                else:
                    print("⚠️ No AI fallback detected")
                
                # Show all citation categories
                categories = [c.get('category', 'unknown') for c in citations]
                category_counts = {}
                for cat in categories:
                    category_counts[cat] = category_counts.get(cat, 0) + 1
                
                print(f"📊 Citation breakdown by category:")
                for cat, count in category_counts.items():
                    print(f"   - {cat}: {count}")
                
                # Check confidence bands
                confidence_bands = data.get('confidenceBands', {})
                if confidence_bands:
                    print(f"📈 Confidence: Low={confidence_bands.get('low', 'N/A'):.2f}, "
                          f"Mid={confidence_bands.get('mid', 'N/A'):.2f}, "
                          f"High={confidence_bands.get('high', 'N/A'):.2f}")
                
                # Metadata
                metadata = data.get('metadata', {})
                if metadata:
                    print(f"⚙️ Processing time: {metadata.get('latencyMs', 'N/A')}ms")
                    print(f"🌐 Language: {metadata.get('language', 'N/A')}")
                    print(f"🤖 Model: {metadata.get('modelVersion', 'N/A')}")
                
            else:
                print(f"❌ Request failed: {response.status_code}")
                print(f"📄 Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
        
        if i < len(scenarios):
            print("-" * 40)
    
    print("\n🏁 Test Complete!")

def test_current_system_status():
    """Check what services are currently failing vs working."""
    print("\n🔍 Checking Current System Status")
    print("=" * 40)
    
    # Test simple payload to see system behavior
    url = "http://localhost:8000/api/v1/checks"
    payload = {
        "inputType": "text",
        "payload": "test simple claim",
        "language": "en"
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            data = response.json()
            citations = data.get('citations', [])
            
            print(f"📊 System returned {len(citations)} citations")
            print("📋 Service status (inferred from citations):")
            
            categories = [c.get('category', 'unknown') for c in citations]
            
            if 'fact_check' in categories:
                print("   ✅ Fact Check API: Working (mock data)")
            else:
                print("   ❌ Fact Check API: No results")
                
            if 'ai_analysis' in categories:
                print("   🤖 Gemini Fallback: Triggered")
            else:
                print("   🤖 Gemini Fallback: Not triggered")
                
            if 'news' in categories:
                print("   📰 News/Reference API: Working")
            else:
                print("   📰 News/Reference API: No results")
                
        else:
            print(f"❌ System check failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ System check error: {str(e)}")

if __name__ == "__main__":
    test_current_system_status()
    test_fallback_scenarios()