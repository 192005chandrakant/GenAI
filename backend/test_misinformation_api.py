"""
Integration tests for the enhanced misinformation detection API endpoints.
Tests the complete API flow including request validation and response formatting.
"""
import pytest
import json
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock, MagicMock

from main import app
from app.models.misinformation_schemas import (
    MisinformationAnalysisRequest,
    MisinformationAnalysisResponse,
    LanguageCode,
    CredibilityBadgeType,
    ProcessingModel,
    ManipulationTechnique,
    ClaimExtraction,
    EvidenceCitation,
    StanceAnalysis,
    StanceType,
    LearnCard
)


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


@pytest.fixture
def mock_enhanced_analysis_response():
    """Mock enhanced analysis response."""
    return MisinformationAnalysisResponse(
        content_id="test_123",
        language=LanguageCode.EN,
        processing_model=ProcessingModel.GEMINI_FLASH,
        claims=[
            ClaimExtraction(
                claim_text="Test claim",
                what="test claim",
                confidence=0.9
            )
        ],
        score=25,
        badge=CredibilityBadgeType.RED,
        verdict="Test verdict - misleading",
        stance_analyses=[
            StanceAnalysis(
                claim_id="claim_0",
                stance=StanceType.REFUTES,
                confidence=0.9,
                evidence_strength=0.85,
                citations=[]
            )
        ],
        citations=[
            EvidenceCitation(
                title="Test Citation",
                url="https://example.com/test",
                snippet="Test snippet",
                source_type="fact_check",
                relevance_score=0.9,
                credibility_weight=0.95,
                recency_weight=0.8
            )
        ],
        explanation="This is a test explanation of why the content is misleading.",
        manipulation_techniques=[ManipulationTechnique.FALSE_CURE],
        learn_card=LearnCard(
            title="Test Learn Card",
            content="This is educational content for testing.",
            tip="Always verify medical claims with authorities.",
            category="health_verification"
        ),
        processing_time=1.23,
        model_escalated=False,
        cache_hit=False
    )


class TestMisinformationAnalysisEndpoint:
    """Test the main analysis endpoint."""
    
    def test_analyze_misinformation_success(self, client, mock_enhanced_analysis_response):
        """Test successful misinformation analysis."""
        request_data = {
            "content": "Drinking hot water every 15 minutes kills coronavirus.",
            "content_type": "text",
            "user_language": "en"
        }
        
        with patch('app.services.gemini_service.enhanced_gemini_service.analyze_misinformation_enhanced') as mock_analyze:
            mock_analyze.return_value = mock_enhanced_analysis_response
            
            response = client.post("/api/v1/misinformation/analyze", json=request_data)
            
            assert response.status_code == 200
            
            data = response.json()
            assert data["content_id"] == "test_123"
            assert data["language"] == "en"
            assert data["score"] == 25
            assert data["badge"] == "red"
            assert data["verdict"] == "Test verdict - misleading"
            assert len(data["claims"]) == 1
            assert len(data["citations"]) == 1
            assert data["manipulation_techniques"] == ["false_cure"]
            assert "learn_card" in data
    
    def test_analyze_misinformation_with_context(self, client, mock_enhanced_analysis_response):
        """Test analysis with additional context."""
        request_data = {
            "content": "Test content with context",
            "content_type": "text",
            "user_language": "en",
            "context": {
                "source": "social_media",
                "user_location": "US"
            }
        }
        
        with patch('app.services.gemini_service.enhanced_gemini_service.analyze_misinformation_enhanced') as mock_analyze:
            mock_analyze.return_value = mock_enhanced_analysis_response
            
            response = client.post("/api/v1/misinformation/analyze", json=request_data)
            
            assert response.status_code == 200
            mock_analyze.assert_called_once()
            
            # Verify context was passed
            call_args = mock_analyze.call_args[0][0]  # First argument (request object)
            assert call_args.context["source"] == "social_media"
            assert call_args.context["user_location"] == "US"
    
    def test_analyze_misinformation_force_pro_model(self, client, mock_enhanced_analysis_response):
        """Test analysis with forced Pro model."""
        request_data = {
            "content": "Complex content requiring Pro model",
            "content_type": "text",
            "force_pro_model": True
        }
        
        # Modify mock response to show Pro model was used
        mock_enhanced_analysis_response.processing_model = ProcessingModel.GEMINI_PRO
        mock_enhanced_analysis_response.model_escalated = True
        
        with patch('app.services.gemini_service.enhanced_gemini_service.analyze_misinformation_enhanced') as mock_analyze:
            mock_analyze.return_value = mock_enhanced_analysis_response
            
            response = client.post("/api/v1/misinformation/analyze", json=request_data)
            
            assert response.status_code == 200
            
            data = response.json()
            assert data["processing_model"] == "gemini-1.5-pro"
            assert data["model_escalated"] is True
    
    def test_analyze_misinformation_validation_error(self, client):
        """Test validation error for invalid request."""
        request_data = {
            "content": "",  # Empty content should fail validation
            "content_type": "invalid_type"
        }
        
        response = client.post("/api/v1/misinformation/analyze", json=request_data)
        
        assert response.status_code == 422  # Validation error
    
    def test_analyze_misinformation_service_error(self, client):
        """Test handling of service errors."""
        request_data = {
            "content": "Test content",
            "content_type": "text"
        }
        
        with patch('app.services.gemini_service.enhanced_gemini_service.analyze_misinformation_enhanced') as mock_analyze:
            mock_analyze.side_effect = Exception("Service unavailable")
            
            response = client.post("/api/v1/misinformation/analyze", json=request_data)
            
            assert response.status_code == 500
            data = response.json()
            assert "Failed to analyze content" in data["detail"]


class TestBatchAnalysisEndpoint:
    """Test the batch analysis endpoint."""
    
    def test_batch_analysis_success(self, client, mock_enhanced_analysis_response):
        """Test successful batch analysis."""
        request_data = {
            "contents": [
                "First claim to analyze",
                "Second claim to analyze"
            ],
            "content_types": ["text", "text"],
            "priority": "normal"
        }
        
        with patch('app.services.gemini_service.enhanced_gemini_service.analyze_misinformation_enhanced') as mock_analyze:
            mock_analyze.return_value = mock_enhanced_analysis_response
            
            response = client.post("/api/v1/misinformation/analyze/batch", json=request_data)
            
            assert response.status_code == 200
            
            data = response.json()
            assert "batch_id" in data
            assert data["total_items"] == 2
            assert data["completed_items"] == 2
            assert data["failed_items"] == 0
            assert data["status"] == "completed"
            assert len(data["results"]) == 2
            
            # Verify analyze was called twice
            assert mock_analyze.call_count == 2
    
    def test_batch_analysis_partial_failure(self, client, mock_enhanced_analysis_response):
        """Test batch analysis with partial failures."""
        request_data = {
            "contents": [
                "Good content",
                "Bad content that fails"
            ]
        }
        
        with patch('app.services.gemini_service.enhanced_gemini_service.analyze_misinformation_enhanced') as mock_analyze:
            # First call succeeds, second fails
            mock_analyze.side_effect = [mock_enhanced_analysis_response, Exception("Analysis failed")]
            
            response = client.post("/api/v1/misinformation/analyze/batch", json=request_data)
            
            assert response.status_code == 200
            
            data = response.json()
            assert data["total_items"] == 2
            assert data["completed_items"] == 1
            assert data["failed_items"] == 1
            assert data["status"] == "partial"
            assert len(data["results"]) == 1  # Only successful results
    
    def test_batch_analysis_empty_request(self, client):
        """Test batch analysis with empty content list."""
        request_data = {
            "contents": []
        }
        
        response = client.post("/api/v1/misinformation/analyze/batch", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["total_items"] == 0
        assert data["completed_items"] == 0


class TestClaimExtractionEndpoint:
    """Test the claim extraction endpoint."""
    
    def test_extract_claims_success(self, client):
        """Test successful claim extraction."""
        with patch('app.services.gemini_service.enhanced_gemini_service.detect_language') as mock_detect, \
             patch('app.services.gemini_service.enhanced_gemini_service.extract_claims') as mock_extract:
            
            mock_detect.return_value = LanguageCode.EN
            mock_extract.return_value = [
                ClaimExtraction(
                    claim_text="Vaccines cause autism",
                    who="Anti-vaccine groups",
                    what="vaccines cause autism",
                    confidence=0.95
                )
            ]
            
            response = client.get(
                "/api/v1/misinformation/claims/extract",
                params={"content": "Vaccines cause autism", "language": "auto"}
            )
            
            assert response.status_code == 200
            
            data = response.json()
            assert data["success"] is True
            assert data["detected_language"] == "en"
            assert len(data["claims"]) == 1
            assert data["claims"][0]["claim_text"] == "Vaccines cause autism"
            assert data["claims"][0]["who"] == "Anti-vaccine groups"
            assert data["total_claims"] == 1
    
    def test_extract_claims_specific_language(self, client):
        """Test claim extraction with specific language."""
        with patch('app.services.gemini_service.enhanced_gemini_service.extract_claims') as mock_extract:
            
            mock_extract.return_value = [
                ClaimExtraction(
                    claim_text="Test claim in Spanish",
                    what="test claim",
                    confidence=0.8
                )
            ]
            
            response = client.get(
                "/api/v1/misinformation/claims/extract",
                params={"content": "Contenido en español", "language": "es"}
            )
            
            assert response.status_code == 200
            
            data = response.json()
            assert data["detected_language"] == "es"  # Should use specified language
    
    def test_extract_claims_error(self, client):
        """Test claim extraction error handling."""
        with patch('app.services.gemini_service.enhanced_gemini_service.detect_language') as mock_detect:
            mock_detect.side_effect = Exception("Service error")
            
            response = client.get(
                "/api/v1/misinformation/claims/extract",
                params={"content": "Test content"}
            )
            
            assert response.status_code == 500


class TestEvidenceSearchEndpoint:
    """Test the evidence search endpoint."""
    
    def test_search_evidence_success(self, client):
        """Test successful evidence search."""
        with patch('app.services.gemini_service.enhanced_gemini_service.retrieve_evidence') as mock_retrieve:
            
            mock_evidence_result = MagicMock()
            mock_evidence_result.query = "test claim"
            mock_evidence_result.sources_searched = ["Google Fact Check API", "Curated Sources"]
            mock_evidence_result.citations_found = [
                EvidenceCitation(
                    title="Test Evidence",
                    url="https://example.com/evidence",
                    snippet="This is test evidence",
                    source_type="fact_check",
                    relevance_score=0.9,
                    credibility_weight=0.95,
                    recency_weight=0.8
                )
            ]
            mock_evidence_result.total_results = 1
            mock_evidence_result.search_time = 0.5
            
            mock_retrieve.return_value = mock_evidence_result
            
            response = client.get(
                "/api/v1/misinformation/evidence/search",
                params={
                    "claims": ["Test claim to search for"],
                    "language": "en",
                    "max_results": 5
                }
            )
            
            assert response.status_code == 200
            
            data = response.json()
            assert data["success"] is True
            assert data["query"] == "test claim"
            assert len(data["sources_searched"]) == 2
            assert len(data["citations"]) == 1
            assert data["citations"][0]["title"] == "Test Evidence"
            assert data["total_results"] == 1
            assert data["search_time"] == 0.5
    
    def test_search_evidence_multiple_claims(self, client):
        """Test evidence search with multiple claims."""
        with patch('app.services.gemini_service.enhanced_gemini_service.retrieve_evidence') as mock_retrieve:
            
            mock_evidence_result = MagicMock()
            mock_evidence_result.citations_found = []
            mock_evidence_result.query = "claim1; claim2"
            mock_evidence_result.sources_searched = []
            mock_evidence_result.total_results = 0
            mock_evidence_result.search_time = 0.1
            
            mock_retrieve.return_value = mock_evidence_result
            
            response = client.get(
                "/api/v1/misinformation/evidence/search",
                params={
                    "claims": ["First claim", "Second claim"],
                    "max_results": 3
                }
            )
            
            assert response.status_code == 200
            
            # Verify that ClaimExtraction objects were created for both claims
            mock_retrieve.assert_called_once()
            call_args = mock_retrieve.call_args[0][0]  # First argument (claims list)
            assert len(call_args) == 2
            assert call_args[0].claim_text == "First claim"
            assert call_args[1].claim_text == "Second claim"


class TestAdminEndpoints:
    """Test admin-only endpoints."""
    
    def test_cache_stats_unauthorized(self, client):
        """Test cache stats without admin access."""
        response = client.get("/api/v1/misinformation/stats/cache")
        
        assert response.status_code == 403
        data = response.json()
        assert "Admin access required" in data["detail"]
    
    def test_cache_stats_authorized(self, client):
        """Test cache stats with admin access."""
        # Mock the get_current_user dependency to return admin user
        with patch('app.api.v1.endpoints.misinformation.get_current_user') as mock_get_user:
            mock_get_user.return_value = {"uid": "admin123", "admin": True}
            
            # Mock cache entries
            with patch('app.services.gemini_service.enhanced_gemini_service.analysis_cache') as mock_cache:
                mock_cache.__len__.return_value = 2
                mock_cache.items.return_value = [
                    ("hash1", MagicMock(
                        created_at=MagicMock(),
                        access_count=5,
                        last_accessed=MagicMock(),
                        result=MagicMock(score=75, badge=MagicMock(value="amber"))
                    )),
                    ("hash2", MagicMock(
                        created_at=MagicMock(),
                        access_count=2,
                        last_accessed=MagicMock(),
                        result=MagicMock(score=25, badge=MagicMock(value="red"))
                    ))
                ]
                
                response = client.get("/api/v1/misinformation/stats/cache")
                
                assert response.status_code == 200
                data = response.json()
                assert data["total_entries"] == 2
                assert len(data["entries"]) == 2
    
    def test_clear_cache_authorized(self, client):
        """Test cache clearing with admin access."""
        with patch('app.api.v1.endpoints.misinformation.get_current_user') as mock_get_user:
            mock_get_user.return_value = {"uid": "admin123", "admin": True}
            
            with patch('app.services.gemini_service.enhanced_gemini_service.analysis_cache') as mock_cache:
                mock_cache.__len__.return_value = 5
                mock_cache.clear = MagicMock()
                
                response = client.post("/api/v1/misinformation/cache/clear")
                
                assert response.status_code == 200
                data = response.json()
                assert data["success"] is True
                assert data["entries_cleared"] == 5
                mock_cache.clear.assert_called_once()


class TestHealthEndpoint:
    """Test health check endpoint."""
    
    def test_health_check_healthy(self, client):
        """Test health check when service is healthy."""
        with patch('app.services.gemini_service.enhanced_gemini_service.flash_model') as mock_model:
            mock_model.__bool__.return_value = True
            
            response = client.get("/api/v1/misinformation/health")
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
            assert data["service"] == "enhanced_misinformation_detection"
            assert "components" in data
    
    def test_health_check_unhealthy(self, client):
        """Test health check when service has issues."""
        with patch('app.services.gemini_service.enhanced_gemini_service.flash_model') as mock_model:
            mock_model.__bool__.return_value = False
            
            response = client.get("/api/v1/misinformation/health")
            
            assert response.status_code == 200
            data = response.json()
            assert data["components"]["gemini_service"] == "unhealthy"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])