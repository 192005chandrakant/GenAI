"""
Mock FAISS Service for development and testing.
"""
from typing import List, Dict, Any

class MockFAISSService:
    """Mock FAISS service for development and testing."""
    
    def __init__(self):
        """Initialize Mock FAISS service."""
        self.claims_db = {}
        self.embeddings_db = {}
    
    async def search_similar_claims(
        self, 
        claims: List[str], 
        k: int = 10, 
        threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """Search for similar claims in mock database."""
        # Return mock results for development
        results = []
        for i, claim in enumerate(claims[:k]):
            results.append({
                "claim_id": f"mock_claim_{i}",
                "similarity": 0.85 - (i * 0.05),
                "distance": 0.15 + (i * 0.05),
                "metadata": {
                    "original_claim": claim,
                    "source": "mock_database",
                    "fact_check_url": f"https://example.com/fact-check/{i}",
                    "verdict": "mixed" if i % 2 else "false",
                    "trust_score": 80 - (i * 5)
                }
            })
        return results
    
    async def add_claim(
        self, 
        claim_id: str, 
        embedding: List[float],
        metadata: Dict[str, Any]
    ):
        """Add a claim to mock index."""
        self.claims_db[claim_id] = metadata
        self.embeddings_db[claim_id] = embedding
    
    async def remove_claim(self, claim_id: str):
        """Remove a claim from mock index."""
        self.claims_db.pop(claim_id, None)
        self.embeddings_db.pop(claim_id, None)
    
    async def get_index_stats(self) -> Dict[str, Any]:
        """Get mock index statistics."""
        return {
            "total_claims": len(self.claims_db),
            "dimension": 768,
            "last_updated": "2025-09-04T15:45:00Z"
        }

# Create service instance
faiss_service = MockFAISSService()
