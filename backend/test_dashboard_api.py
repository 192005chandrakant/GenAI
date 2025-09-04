"""
Simple script to verify that the dashboard routes are implemented correctly.
"""
import json
import requests

BASE_URL = "http://localhost:8000"

def test_dashboard_endpoints():
    """Test the dashboard endpoints."""
    endpoints = [
        "/api/v1/dashboard/status",
        "/api/v1/dashboard/health",
        "/api/v1/dashboard/live",
        "/api/v1/dashboard/metrics",
        "/api/v1/dashboard/services",
        "/api/v1/dashboard/analytics",
        "/api/v1/dashboard/config",
        "/api/v1/dashboard/routes",
        "/api/v1/dashboard/api-info"
    ]
    
    results = {}
    
    print(f"Testing dashboard endpoints at {BASE_URL}")
    print("-" * 50)
    
    for endpoint in endpoints:
        url = f"{BASE_URL}{endpoint}"
        print(f"Testing endpoint: {url}")
        
        try:
            response = requests.get(url, timeout=10)
            status_code = response.status_code
            
            if status_code == 200:
                print(f"✅ SUCCESS: {endpoint} - Status {status_code}")
                # Print a sample of the JSON response
                try:
                    data = response.json()
                    sample = json.dumps(data, indent=2)[:200] + "..." if len(json.dumps(data)) > 200 else json.dumps(data, indent=2)
                    print(f"Response sample: {sample}")
                except:
                    print("Response is not JSON format")
            else:
                print(f"❌ FAIL: {endpoint} - Status {status_code}")
                print(f"Response: {response.text[:100]}")
            
            results[endpoint] = {
                "status": status_code,
                "success": status_code == 200
            }
        except Exception as e:
            print(f"❌ ERROR: {endpoint} - {str(e)}")
            results[endpoint] = {
                "status": "error",
                "success": False,
                "error": str(e)
            }
        
        print("-" * 50)
    
    # Print summary
    success_count = sum(1 for r in results.values() if r["success"])
    print(f"Summary: {success_count}/{len(endpoints)} endpoints working correctly")
    
    return results

if __name__ == "__main__":
    test_dashboard_endpoints()
