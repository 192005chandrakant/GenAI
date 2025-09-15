"""
Test cases for enhanced misinformation detection features.
Tests the complete pipeline from claim extraction to final verdict generation.
"""
import pytest
import json
from datetime import datetime
from unittest.mock import AsyncMock, patch, MagicMock

from app.models.misinformation_schemas import (
    MisinformationAnalysisRequest,
    MisinformationAnalysisResponse,
    ClaimExtraction,
    EvidenceCitation,
    StanceAnalysis,
    StanceType,
    CredibilityBadgeType,
    ManipulationTechnique,
    ProcessingModel,
    LanguageCode,
    LearnCard
)
from app.services.gemini_service import EnhancedGeminiService


@pytest.fixture
def enhanced_gemini_service():
    """Create a mock EnhancedGeminiService for testing."""
    service = EnhancedGeminiService()
    # Mock the AI models to avoid real API calls
    service.flash_model = MagicMock()
    service.pro_model = MagicMock()
    service.vision_model = MagicMock()
    service.embedding_model = "models/embedding-001"
    service.http_client = AsyncMock()
    return service


@pytest.fixture
def sample_misinformation_request():
    """Sample request for testing."""
    return MisinformationAnalysisRequest(
        content="Drinking hot water every 15 minutes kills coronavirus.",
        content_type="text",
        user_language=LanguageCode.EN,
        context={"test": True}
    )


@pytest.fixture
def sample_claims():
    """Sample extracted claims for testing."""
    return [
        ClaimExtraction(
            claim_text="Drinking hot water every 15 minutes kills coronavirus",
            who=None,
            what="hot water kills coronavirus",
            where=None,
            when=None,
            confidence=0.9
        )
    ]


@pytest.fixture
def sample_citations():
    """Sample evidence citations for testing."""
    return [
        EvidenceCitation(
            title="WHO Mythbusters",
            url="https://www.who.int/emergencies/diseases/novel-coronavirus-2019/advice-for-public/myth-busters",
            snippet="Drinking hot water does not kill coronavirus.",
            date=datetime(2020, 4, 15),
            source_type="fact_check",
            relevance_score=0.95,
            credibility_weight=0.98,
            recency_weight=0.6
        ),
        EvidenceCitation(
            title="CDC Guidance on COVID-19 Prevention",
            url="https://www.cdc.gov/coronavirus/2019-ncov/prevent-getting-sick",
            snippet="Prevent infection by vaccination, masking, and hygiene—not hot water.",
            date=datetime(2021, 3, 20),
            source_type="government",
            relevance_score=0.88,
            credibility_weight=0.95,
            recency_weight=0.7
        )
    ]


class TestLanguageDetection:
    """Test language detection functionality."""
    
    @pytest.mark.asyncio
    async def test_detect_language_english(self, enhanced_gemini_service):
        """Test detecting English language."""
        with patch.object(enhanced_gemini_service, '_generate_flash_response') as mock_response:
            mock_response.return_value = "en"
            
            result = await enhanced_gemini_service.detect_language("This is an English text.")
            
            assert result == LanguageCode.EN
            mock_response.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_detect_language_spanish(self, enhanced_gemini_service):
        """Test detecting Spanish language."""
        with patch.object(enhanced_gemini_service, '_generate_flash_response') as mock_response:
            mock_response.return_value = "es"
            
            result = await enhanced_gemini_service.detect_language("Este es un texto en español.")
            
            assert result == LanguageCode.ES
            mock_response.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_detect_language_fallback(self, enhanced_gemini_service):
        """Test language detection fallback to English."""
        with patch.object(enhanced_gemini_service, '_generate_flash_response') as mock_response:
            mock_response.return_value = "unknown"
            
            result = await enhanced_gemini_service.detect_language("Some text.")
            
            assert result == LanguageCode.EN  # Should fallback to English


class TestClaimExtraction:
    """Test claim extraction functionality."""
    
    @pytest.mark.asyncio
    async def test_extract_claims_success(self, enhanced_gemini_service):
        """Test successful claim extraction."""
        mock_response = json.dumps({
            "claims": [
                {
                    "claim_text": "Hot water kills coronavirus",
                    "who": None,
                    "what": "hot water kills coronavirus",
                    "where": None,
                    "when": None,
                    "confidence": 0.9
                }
            ]
        })
        
        with patch.object(enhanced_gemini_service, '_generate_flash_response') as mock_generate:
            mock_generate.return_value = mock_response
            
            result = await enhanced_gemini_service.extract_claims(
                "Hot water kills coronavirus", 
                LanguageCode.EN
            )
            
            assert len(result) == 1
            assert result[0].claim_text == "Hot water kills coronavirus"
            assert result[0].confidence == 0.9
    
    @pytest.mark.asyncio
    async def test_extract_claims_multiple(self, enhanced_gemini_service):
        """Test extracting multiple claims."""
        mock_response = json.dumps({
            "claims": [
                {
                    "claim_text": "Vaccines cause autism",
                    "who": "Anti-vaccine groups",
                    "what": "vaccines cause autism",
                    "where": None,
                    "when": None,
                    "confidence": 0.95
                },
                {
                    "claim_text": "5G towers spread COVID-19",
                    "who": "Conspiracy theorists",
                    "what": "5G towers spread COVID-19",
                    "where": "Globally",
                    "when": "2020",
                    "confidence": 0.88
                }
            ]
        })
        
        with patch.object(enhanced_gemini_service, '_generate_flash_response') as mock_generate:
            mock_generate.return_value = mock_response
            
            result = await enhanced_gemini_service.extract_claims(
                "Vaccines cause autism and 5G towers spread COVID-19", 
                LanguageCode.EN
            )
            
            assert len(result) == 2
            assert result[0].who == "Anti-vaccine groups"
            assert result[1].where == "Globally"
    
    @pytest.mark.asyncio
    async def test_extract_claims_error_handling(self, enhanced_gemini_service):
        """Test claim extraction error handling."""
        with patch.object(enhanced_gemini_service, '_generate_flash_response') as mock_generate:
            mock_generate.side_effect = Exception("API Error")
            
            result = await enhanced_gemini_service.extract_claims(
                "Some content", 
                LanguageCode.EN
            )
            
            assert result == []  # Should return empty list on error


class TestEvidenceRetrieval:
    """Test evidence retrieval functionality."""
    
    @pytest.mark.asyncio
    async def test_retrieve_evidence_success(self, enhanced_gemini_service, sample_claims):
        """Test successful evidence retrieval."""
        # Mock fact check API response
        mock_api_response = MagicMock()
        mock_api_response.status_code = 200
        mock_api_response.json.return_value = {
            "claims": [
                {
                    "text": "Hot water kills coronavirus",
                    "claimReview": [
                        {
                            "title": "Fact Check: Hot Water Claims",
                            "url": "https://example.com/factcheck",
                            "reviewDate": "2020-04-15"
                        }
                    ]
                }
            ]
        }
        
        enhanced_gemini_service.http_client.get = AsyncMock(return_value=mock_api_response)
        enhanced_gemini_service.fact_check_api_key = "test-key"
        
        result = await enhanced_gemini_service.retrieve_evidence(sample_claims)
        
        assert len(result.citations_found) > 0
        assert result.sources_searched
        assert "Google Fact Check Tools API" in result.sources_searched
    
    @pytest.mark.asyncio
    async def test_retrieve_evidence_api_failure(self, enhanced_gemini_service, sample_claims):
        """Test evidence retrieval when external APIs fail."""
        # Mock API failure
        enhanced_gemini_service.http_client.get = AsyncMock(side_effect=Exception("API Error"))
        enhanced_gemini_service.fact_check_api_key = "test-key"
        
        result = await enhanced_gemini_service.retrieve_evidence(sample_claims)
        
        # Should still return result with curated sources
        assert isinstance(result.citations_found, list)
        assert result.search_time > 0


class TestStanceAnalysis:
    """Test stance analysis functionality."""
    
    @pytest.mark.asyncio
    async def test_analyze_stance_refutes(self, enhanced_gemini_service, sample_claims, sample_citations):
        """Test stance analysis that refutes claims."""
        mock_response = json.dumps({
            "stance": "refutes",
            "confidence": 0.92,
            "evidence_strength": 0.95,
            "reasoning": "Strong evidence contradicts the claim"
        })
        
        with patch.object(enhanced_gemini_service, '_generate_flash_response') as mock_generate:
            mock_generate.return_value = mock_response
            
            result = await enhanced_gemini_service.analyze_stance(sample_claims, sample_citations)
            
            assert len(result) == 1
            assert result[0].stance == StanceType.REFUTES
            assert result[0].confidence == 0.92
            assert result[0].evidence_strength == 0.95
    
    @pytest.mark.asyncio
    async def test_analyze_stance_supports(self, enhanced_gemini_service, sample_claims, sample_citations):
        """Test stance analysis that supports claims."""
        mock_response = json.dumps({
            "stance": "supports",
            "confidence": 0.85,
            "evidence_strength": 0.78,
            "reasoning": "Evidence supports the claim"
        })
        
        with patch.object(enhanced_gemini_service, '_generate_flash_response') as mock_generate:
            mock_generate.return_value = mock_response
            
            result = await enhanced_gemini_service.analyze_stance(sample_claims, sample_citations)
            
            assert len(result) == 1
            assert result[0].stance == StanceType.SUPPORTS
    
    @pytest.mark.asyncio
    async def test_analyze_stance_needs_context(self, enhanced_gemini_service, sample_claims, sample_citations):
        """Test stance analysis that needs context."""
        mock_response = json.dumps({
            "stance": "needs_context",
            "confidence": 0.75,
            "evidence_strength": 0.68,
            "reasoning": "Evidence is mixed and requires context"
        })
        
        with patch.object(enhanced_gemini_service, '_generate_flash_response') as mock_generate:
            mock_generate.return_value = mock_response
            
            result = await enhanced_gemini_service.analyze_stance(sample_claims, sample_citations)
            
            assert len(result) == 1
            assert result[0].stance == StanceType.NEEDS_CONTEXT


class TestVerdictGeneration:
    """Test verdict generation functionality."""
    
    @pytest.mark.asyncio
    async def test_generate_verdict_misleading(self, enhanced_gemini_service, sample_claims):
        """Test generating a misleading verdict."""
        mock_stance_analyses = [
            StanceAnalysis(
                claim_id="claim_0",
                stance=StanceType.REFUTES,
                confidence=0.92,
                evidence_strength=0.95,
                citations=[]
            )
        ]
        
        mock_response = json.dumps({
            "score": 15,
            "badge": "red",
            "verdict": "Misleading health claim",
            "explanation": "This uses false health advice without scientific basis. Technique: 'false cure' misinformation.",
            "manipulation_techniques": ["false_cure"],
            "learn_card": {
                "title": "Health Misinformation",
                "content": "Always verify medical advice with WHO/CDC before sharing.",
                "tip": "Check with medical authorities for health claims.",
                "category": "health_verification"
            }
        })
        
        with patch.object(enhanced_gemini_service, '_generate_flash_response') as mock_generate:
            mock_generate.return_value = mock_response
            
            result = await enhanced_gemini_service.generate_verdict(
                sample_claims, mock_stance_analyses, [], use_pro_model=False
            )
            
            assert result["score"] == 15
            assert result["badge"] == "red"
            assert "false_cure" in result["manipulation_techniques"]
            assert "learn_card" in result
    
    @pytest.mark.asyncio
    async def test_generate_verdict_trustworthy(self, enhanced_gemini_service, sample_claims):
        """Test generating a trustworthy verdict."""
        mock_stance_analyses = [
            StanceAnalysis(
                claim_id="claim_0",
                stance=StanceType.SUPPORTS,
                confidence=0.95,
                evidence_strength=0.98,
                citations=[]
            )
        ]
        
        mock_response = json.dumps({
            "score": 88,
            "badge": "green",
            "verdict": "Accurate information",
            "explanation": "This claim is well-supported by reliable scientific evidence.",
            "manipulation_techniques": [],
            "learn_card": {
                "title": "Source Verification",
                "content": "This shows how to verify claims with authoritative sources.",
                "tip": "Always check multiple reliable sources.",
                "category": "source_verification"
            }
        })
        
        with patch.object(enhanced_gemini_service, '_generate_flash_response') as mock_generate:
            mock_generate.return_value = mock_response
            
            result = await enhanced_gemini_service.generate_verdict(
                sample_claims, mock_stance_analyses, [], use_pro_model=False
            )
            
            assert result["score"] == 88
            assert result["badge"] == "green"
            assert result["manipulation_techniques"] == []


class TestCaching:
    """Test caching functionality."""
    
    def test_generate_content_hash(self, enhanced_gemini_service):
        """Test content hash generation."""
        content = "Test content"
        hash1 = enhanced_gemini_service._generate_content_hash(content, "text")
        hash2 = enhanced_gemini_service._generate_content_hash(content, "text")
        hash3 = enhanced_gemini_service._generate_content_hash("Different content", "text")
        
        assert hash1 == hash2  # Same content should produce same hash
        assert hash1 != hash3  # Different content should produce different hash
        assert len(hash1) == 64  # SHA-256 produces 64 character hex string
    
    @pytest.mark.asyncio
    async def test_cache_miss_and_hit(self, enhanced_gemini_service, sample_misinformation_request):
        """Test cache miss followed by cache hit."""
        # Mock the complete analysis flow
        with patch.object(enhanced_gemini_service, 'detect_language') as mock_detect, \
             patch.object(enhanced_gemini_service, 'extract_claims') as mock_extract, \
             patch.object(enhanced_gemini_service, 'retrieve_evidence') as mock_retrieve, \
             patch.object(enhanced_gemini_service, 'analyze_stance') as mock_stance, \
             patch.object(enhanced_gemini_service, 'generate_verdict') as mock_verdict:
            
            # Setup mocks
            mock_detect.return_value = LanguageCode.EN
            mock_extract.return_value = []
            mock_retrieve.return_value = MagicMock(citations_found=[])
            mock_stance.return_value = []
            mock_verdict.return_value = {
                "score": 50,
                "badge": "amber",
                "verdict": "Test verdict",
                "explanation": "Test explanation",
                "manipulation_techniques": [],
                "learn_card": {
                    "title": "Test",
                    "content": "Test content",
                    "tip": "Test tip",
                    "category": "test"
                }
            }
            
            # First call - should be cache miss
            result1 = await enhanced_gemini_service.analyze_misinformation_enhanced(sample_misinformation_request)
            assert not result1.cache_hit
            
            # Second call - should be cache hit
            result2 = await enhanced_gemini_service.analyze_misinformation_enhanced(sample_misinformation_request)
            assert result2.cache_hit
            
            # Verify analysis was only called once (for the first request)
            assert mock_detect.call_count == 1
            assert mock_extract.call_count == 1


class TestEscalationLogic:
    """Test model escalation logic."""
    
    def test_should_escalate_force_pro(self, enhanced_gemini_service):
        """Test forced escalation to Pro model."""
        result = enhanced_gemini_service._should_escalate_to_pro([], [], force_pro=True)
        assert result is True
    
    def test_should_escalate_many_claims(self, enhanced_gemini_service):
        """Test escalation due to many claims."""
        many_claims = [ClaimExtraction(claim_text=f"Claim {i}", what=f"claim {i}", confidence=0.8) for i in range(5)]
        result = enhanced_gemini_service._should_escalate_to_pro(many_claims, [])
        assert result is True
    
    def test_should_escalate_conflicting_evidence(self, enhanced_gemini_service):
        """Test escalation due to conflicting evidence."""
        conflicting_stances = [
            StanceAnalysis(claim_id="1", stance=StanceType.NEEDS_CONTEXT, confidence=0.7, evidence_strength=0.6, citations=[]),
            StanceAnalysis(claim_id="2", stance=StanceType.NEEDS_CONTEXT, confidence=0.8, evidence_strength=0.7, citations=[])
        ]
        result = enhanced_gemini_service._should_escalate_to_pro([], conflicting_stances)
        assert result is True
    
    def test_should_escalate_low_confidence(self, enhanced_gemini_service):
        """Test escalation due to low confidence."""
        low_confidence_stances = [
            StanceAnalysis(claim_id="1", stance=StanceType.SUPPORTS, confidence=0.5, evidence_strength=0.6, citations=[])
        ]
        result = enhanced_gemini_service._should_escalate_to_pro([], low_confidence_stances)
        assert result is True
    
    def test_should_not_escalate(self, enhanced_gemini_service):
        """Test no escalation for simple, confident analysis."""
        simple_claims = [ClaimExtraction(claim_text="Simple claim", what="simple claim", confidence=0.9)]
        confident_stances = [
            StanceAnalysis(claim_id="1", stance=StanceType.SUPPORTS, confidence=0.9, evidence_strength=0.85, citations=[])
        ]
        result = enhanced_gemini_service._should_escalate_to_pro(simple_claims, confident_stances, force_pro=False)
        assert result is False


class TestFullAnalysisPipeline:
    """Test the complete misinformation analysis pipeline."""
    
    @pytest.mark.asyncio
    async def test_full_analysis_pipeline(self, enhanced_gemini_service):
        """Test the complete analysis from request to response."""
        request = MisinformationAnalysisRequest(
            content="The Earth is flat and NASA is hiding the truth.",
            content_type="text",
            user_language=LanguageCode.EN
        )
        
        # Mock all components of the pipeline
        with patch.object(enhanced_gemini_service, 'detect_language') as mock_detect, \
             patch.object(enhanced_gemini_service, 'extract_claims') as mock_extract, \
             patch.object(enhanced_gemini_service, 'retrieve_evidence') as mock_retrieve, \
             patch.object(enhanced_gemini_service, 'analyze_stance') as mock_stance, \
             patch.object(enhanced_gemini_service, 'generate_verdict') as mock_verdict, \
             patch.object(enhanced_gemini_service, '_should_escalate_to_pro') as mock_escalate:
            
            # Setup mock returns
            mock_detect.return_value = LanguageCode.EN
            mock_extract.return_value = [
                ClaimExtraction(
                    claim_text="The Earth is flat",
                    what="Earth is flat",
                    confidence=0.95
                )
            ]
            mock_retrieve.return_value = MagicMock(citations_found=[
                EvidenceCitation(
                    title="Scientific Evidence for Spherical Earth",
                    url="https://example.com/science",
                    snippet="Multiple lines of evidence confirm Earth is spherical",
                    source_type="academic",
                    relevance_score=0.98,
                    credibility_weight=0.95,
                    recency_weight=0.9
                )
            ])
            mock_stance.return_value = [
                StanceAnalysis(
                    claim_id="claim_0",
                    stance=StanceType.REFUTES,
                    confidence=0.98,
                    evidence_strength=0.96,
                    citations=[]
                )
            ]
            mock_verdict.return_value = {
                "score": 5,
                "badge": "red",
                "verdict": "Conspiracy theory - scientifically false",
                "explanation": "This is a well-debunked conspiracy theory that contradicts overwhelming scientific evidence.",
                "manipulation_techniques": ["conspiracy_theory"],
                "learn_card": {
                    "title": "Scientific Consensus",
                    "content": "Learn how scientific consensus is established through peer review and evidence.",
                    "tip": "Trust established scientific institutions over conspiracy theories.",
                    "category": "scientific_literacy"
                }
            }
            mock_escalate.return_value = False
            
            # Execute the full pipeline
            result = await enhanced_gemini_service.analyze_misinformation_enhanced(request)
            
            # Verify the result structure
            assert isinstance(result, MisinformationAnalysisResponse)
            assert result.language == LanguageCode.EN
            assert result.processing_model == ProcessingModel.GEMINI_FLASH
            assert len(result.claims) == 1
            assert result.score == 5
            assert result.badge == CredibilityBadgeType.RED
            assert ManipulationTechnique.CONSPIRACY_THEORY in result.manipulation_techniques
            assert isinstance(result.learn_card, LearnCard)
            assert result.processing_time > 0
            assert not result.model_escalated
    
    @pytest.mark.asyncio
    async def test_analysis_with_escalation(self, enhanced_gemini_service):
        """Test analysis that triggers escalation to Pro model."""
        request = MisinformationAnalysisRequest(
            content="Complex claim with ambiguous evidence",
            force_pro_model=True
        )
        
        with patch.object(enhanced_gemini_service, 'detect_language') as mock_detect, \
             patch.object(enhanced_gemini_service, 'extract_claims') as mock_extract, \
             patch.object(enhanced_gemini_service, 'retrieve_evidence') as mock_retrieve, \
             patch.object(enhanced_gemini_service, 'analyze_stance') as mock_stance, \
             patch.object(enhanced_gemini_service, 'generate_verdict') as mock_verdict:
            
            # Setup mock returns for complex analysis
            mock_detect.return_value = LanguageCode.EN
            mock_extract.return_value = [
                ClaimExtraction(claim_text="Complex claim", what="complex claim", confidence=0.6)
            ]
            mock_retrieve.return_value = MagicMock(citations_found=[])
            mock_stance.return_value = [
                StanceAnalysis(
                    claim_id="claim_0",
                    stance=StanceType.NEEDS_CONTEXT,
                    confidence=0.6,
                    evidence_strength=0.5,
                    citations=[]
                )
            ]
            mock_verdict.return_value = {
                "score": 45,
                "badge": "amber",
                "verdict": "Requires additional context",
                "explanation": "The available evidence is insufficient to make a definitive assessment.",
                "manipulation_techniques": [],
                "learn_card": {
                    "title": "Incomplete Information",
                    "content": "Learn to recognize when claims need more investigation.",
                    "tip": "Seek additional sources when evidence is limited.",
                    "category": "critical_thinking"
                }
            }
            
            result = await enhanced_gemini_service.analyze_misinformation_enhanced(request)
            
            # Should use Pro model due to force_pro_model=True
            assert result.model_escalated is True
            assert result.processing_model == ProcessingModel.GEMINI_PRO


if __name__ == "__main__":
    pytest.main([__file__, "-v"])