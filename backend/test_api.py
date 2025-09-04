"""
Test script to verify the backend API is working correctly.
"""
import asyncio
import json
from app.api.v1.endpoints.checks import create_check
from app.models.content_schemas import CheckRequest, InputType, Language

async def test_api():
    """Test the main check endpoint."""
    print("Testing the Misinformation Detection API...")
    
    # Create a test request
    test_request = CheckRequest(
        payload="The Earth is flat and NASA is hiding the truth.",
        inputType=InputType.TEXT,
        language=Language.EN
    )
    
    try:
        # Mock background tasks
        class MockBackgroundTasks:
            def add_task(self, func, *args, **kwargs):
                pass
        
        background_tasks = MockBackgroundTasks()
        
        # Call the API endpoint
        result = await create_check(
            request=test_request,
            background_tasks=background_tasks,
            current_user=None
        )
        
        print("✅ API Test Successful!")
        print(f"Check ID: {result.id}")
        print(f"Score: {result.score}")
        print(f"Badge: {result.badge}")
        print(f"Verdict: {result.verdict}")
        print(f"Number of claims: {len(result.claims)}")
        print(f"Number of citations: {len(result.citations)}")
        print(f"Number of learn cards: {len(result.learnCards)}")
        
        return True
        
    except Exception as e:
        print(f"❌ API Test Failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_api())
    if success:
        print("\n🎉 Backend is fully functional!")
    else:
        print("\n❌ Backend has issues.")
