"""
Check endpoints for the AI-powered misinformation detection system.
Implements the main /v1/checks API as specified in the roadmap.
"""
import logging
import hashlib
import time
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse

from app.models.dto import (
    ConfidenceBands, StanceStats, CheckMetadata, BadgeColor,
    StanceType, HealthResponse, Citation, SourceCategory, CheckRequest, CheckResponse
)
from app.models.check_result_schemas import (
    VerdictType
)
from app.models.learning_schemas import LearnCard
from app.models.content_schemas import Claim
from app.core.config import settings
from app.services.firestore_service import firestore_service
from app.services.gemini_service import gemini_service
from app.services.vertex_ai_service import vertex_ai_service
from app.services.translation_service import translation_service
from app.services.fact_check_service import fact_check_service
from app.services.faiss_service import faiss_service
from app.auth.firebase import verify_firebase_token
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)
router = APIRouter()


def get_current_user(token: Optional[str] = None):
    """Get current user from Firebase token (optional)."""
    if not token:
        return None
    try:
        return verify_firebase_token(token)
    except Exception as e:
        logger.warning(f"Invalid token: {e}")
        return None


from app.services.gemini_service import gemini_service


def _convert_verdict_to_stance(verdict: str) -> StanceType:
    """Convert Gemini verdict to StanceType."""
    verdict_upper = verdict.upper()
    if verdict_upper in ["ACCURATE", "MOSTLY_ACCURATE"]:
        return StanceType.SUPPORT
    elif verdict_upper in ["INACCURATE", "MOSTLY_INACCURATE"]:
        return StanceType.REFUTE
    elif verdict_upper == "MIXED":
        return StanceType.COMMENT
    else:  # UNVERIFIABLE or unknown
        return StanceType.UNRELATED


async def extract_claims_service(content: str, language: str) -> list[Claim]:
    """Extract claims from content using Gemini Flash."""
    try:
        if settings.use_mocks:
            # Return mock claims for development
            return [
                Claim(
                    who="Mock Person",
                    what="Made a statement about something",
                    where="Mock Location",
                    when="2025-09-01",
                    confidence=0.85
                )
            ]
        
        # Use Gemini Flash for claim extraction
        claims_data = await gemini_service.extract_claims(content, language)
        claims = []
        
        for claim_data in claims_data:
            claim = Claim(
                who=claim_data.get("who"),
                what=claim_data.get("what", ""),
                where=claim_data.get("where"),
                when=claim_data.get("when"),
                confidence=claim_data.get("confidence", 0.5)
            )
            claims.append(claim)
        
        return claims
    except Exception as e:
        logger.error(f"Error extracting claims: {e}")
        return []


async def retrieve_evidence_service(claims: list[Claim], language: str) -> list[Citation]:
    """Retrieve evidence using multiple sources."""
    try:
        citations = []
        
        if settings.use_mocks:
            # Return mock citations for development
            return [
                Citation(
                    title="Mock Fact Check Article",
                    url="https://example.com/fact-check",
                    domain="example.com",
                    timestamp=datetime.utcnow(),
                    stance=StanceType.REFUTE,
                    excerpt="This is a mock excerpt from a fact-checking article.",
                    trustScore=85,
                    category="fact_check"
                )
            ]
        
        # 1. Vertex AI Grounding (using analyze_text_content as fallback)
        grounding_results = []
        try:
            # Use existing text analysis method as grounding substitute
            for claim in claims:
                result = await vertex_ai_service.analyze_text_content(
                    claim.what, language
                )
                # Extract citations if any are returned
                if hasattr(result, 'citations') and result.citations:
                    grounding_results.extend(result.citations)
            citations.extend(grounding_results)
        except Exception as e:
            logger.warning(f"Grounding search failed: {e}")

        # 2. Fact Check Tools API
        fact_check_results = []
        try:
            fact_check_results = await fact_check_service.search_fact_checks(
                " ".join([claim.what for claim in claims])  # Combine claims into single query
            )
            citations.extend(fact_check_results)
        except Exception as e:
            logger.warning(f"Fact check search failed: {e}")

        # 3. FAISS similarity search
        faiss_results = []
        try:
            faiss_results = await faiss_service.search_similar_claims(
                [claim.what for claim in claims]
            )
            citations.extend(faiss_results)
        except Exception as e:
            logger.warning(f"FAISS search failed: {e}")        # 4. Gemini Fallback - Primary fallback when other APIs fail
        # Track which services failed or returned insufficient data
        service_failures = []
        if not grounding_results:
            service_failures.append("Vertex AI Grounding")
        if not fact_check_results:
            service_failures.append("Fact Check API")
        if not faiss_results:
            service_failures.append("FAISS Search")
        
        # In mock mode, also trigger fallback to demonstrate functionality  
        # or when we have very limited results (< 2 citations total)
        total_citations_so_far = len(citations)
        should_use_fallback = (
            len(service_failures) > 0 or  # Any service failed
            (settings.use_mocks and total_citations_so_far < 2) or  # Mock mode with very limited results
            total_citations_so_far == 0  # No results at all
        )
        
        if should_use_fallback:
            try:
                if service_failures:
                    logger.info(f"🔄 Triggering Gemini fallback due to failed services: {', '.join(service_failures)}")
                else:
                    logger.info(f"🔄 Triggering Gemini fallback due to insufficient evidence (mock mode or limited results: {total_citations_so_far})")
                
                # Use the first claim or combine all claims for analysis
                main_content = claims[0].what if claims else ""
                if len(claims) > 1:
                    main_content = " ".join([claim.what for claim in claims])
                
                # Get fallback analysis from Gemini
                gemini_analysis = await gemini_service.fact_check_fallback(
                    content=main_content,
                    content_type="text",
                    context={
                        "language": language,
                        "source": "user_input",
                        "claims_count": len(claims),
                        "failed_services": service_failures,
                        "mock_mode": settings.use_mocks,
                        "existing_citations": total_citations_so_far
                    }
                )
                
                if gemini_analysis.get("success"):
                    # Convert Gemini analysis to Citation format
                    gemini_citation = Citation(
                        title=f"AI Analysis: {gemini_analysis.get('verdict', 'Analysis')}",
                        url="https://ai.google.dev/gemini-api",
                        domain="ai.google.dev",
                        timestamp=datetime.utcnow(),
                        stance=_convert_verdict_to_stance(gemini_analysis.get('verdict', 'UNVERIFIABLE')),
                        excerpt=gemini_analysis.get('summary', 'AI-powered analysis of the provided content'),
                        trustScore=int(gemini_analysis.get('credibility_score', 0.5) * 100),
                        category=SourceCategory.AI_ANALYSIS
                    )
                    citations.append(gemini_citation)
                    
                    # Add additional citations from Gemini analysis if available
                    for citation_data in gemini_analysis.get('citations', []):
                        if citation_data.get('url') and citation_data.get('title'):
                            citations.append(Citation(
                                title=citation_data['title'],
                                url=citation_data['url'],
                                domain=citation_data.get('url', '').replace('https://', '').replace('http://', '').split('/')[0],
                                timestamp=datetime.utcnow(),
                                stance=StanceType.SUPPORT,  # Default to support for AI-recommended sources
                                excerpt=citation_data.get('snippet', ''),
                                trustScore=int(citation_data.get('relevance_score', 0.8) * 100),
                                category=SourceCategory.NEWS  # Default to news for AI-recommended sources
                            ))
                    
                    logger.info(f"✅ Gemini fallback provided {len(gemini_analysis.get('citations', [])) + 1} citations to compensate for insufficient evidence")
                else:
                    logger.warning(f"⚠️ Gemini fallback failed: {gemini_analysis.get('error', 'Unknown error')}")
                    
            except Exception as e:
                logger.error(f"❌ Gemini fallback error: {str(e)}")
        else:
            logger.info("✅ Sufficient evidence from primary services - Gemini fallback not needed")

        # Remove duplicates and sort by trust score
        unique_citations = {}
        for citation in citations:
            key = f"{citation.domain}:{citation.url}"
            if key not in unique_citations or citation.trustScore > unique_citations[key].trustScore:
                unique_citations[key] = citation
        
        return sorted(unique_citations.values(), key=lambda x: x.trustScore, reverse=True)[:5]
        
    except Exception as e:
        logger.error(f"Error retrieving evidence: {e}")
        return []


async def analyze_stance_service(claims: list[Claim], citations: list[Citation]) -> StanceStats:
    """Analyze stance distribution using ONNX model."""
    try:
        if settings.use_mocks or not citations:
            return StanceStats(support=0.3, refute=0.5, neutral=0.2)
        
        # Count stances from citations
        support_count = len([c for c in citations if c.stance == StanceType.SUPPORT])
        refute_count = len([c for c in citations if c.stance == StanceType.REFUTE])
        neutral_count = len([c for c in citations if c.stance == StanceType.NEUTRAL])
        
        total = support_count + refute_count + neutral_count
        if total == 0:
            return StanceStats(support=0.0, refute=0.0, neutral=1.0)
        
        return StanceStats(
            support=support_count / total,
            refute=refute_count / total,
            neutral=neutral_count / total
        )
    except Exception as e:
        logger.error(f"Error analyzing stance: {e}")
        return StanceStats(support=0.0, refute=0.0, neutral=1.0)


async def generate_verdict_service(
    score: int, 
    stance_stats: StanceStats, 
    citations: list[Citation],
    language: str
) -> tuple[str, BadgeColor]:
    """Generate verdict and badge color."""
    try:
        # Determine badge color based on score
        if score >= 80:
            badge = BadgeColor.GREEN
            verdict_base = "Likely accurate"
        elif score >= 40:
            badge = BadgeColor.YELLOW
            verdict_base = "Needs context"
        else:
            badge = BadgeColor.RED
            verdict_base = "Likely misleading"
        
        # Add reasoning based on evidence
        if not citations:
            verdict = f"{verdict_base} - insufficient evidence found"
        elif stance_stats.refute > 0.6:
            verdict = f"{verdict_base} - strong counter-evidence found"
        elif stance_stats.support > 0.6:
            verdict = f"{verdict_base} - supporting evidence found"
        else:
            verdict = f"{verdict_base} - mixed evidence requires careful evaluation"
        
        return verdict, badge
        
    except Exception as e:
        logger.error(f"Error generating verdict: {e}")
        return "Analysis incomplete", BadgeColor.YELLOW


async def get_learn_cards_service(
    claims: list[Claim], 
    citations: list[Citation], 
    language: str
) -> list[LearnCard]:
    """Get educational learn cards based on detected patterns."""
    try:
        if settings.use_mocks:
            return [
                LearnCard(
                    technique="Cherry picking",
                    explanation="Selectively presenting facts that support a position while ignoring contradictory evidence",
                    example="Showing only positive reviews while hiding negative ones",
                    tips=["Look for missing context", "Check for counter-evidence"],
                    category="logical_fallacy",
                    difficulty="beginner"
                )
            ]
        
        # Get lessons from Firestore based on detected patterns
        learn_cards = await firestore_service.get_relevant_lessons(claims, citations, language)
        return learn_cards[:3]  # Limit to 3 cards
        
    except Exception as e:
        logger.error(f"Error getting learn cards: {e}")
        return []


def calculate_risk_score(
    stance_stats: StanceStats, 
    citations: list[Citation],
    claims: list[Claim]
) -> tuple[int, ConfidenceBands]:
    """Calculate risk score and confidence bands."""
    try:
        # Base score calculation
        if not citations:
            base_score = 50  # Neutral when no evidence
        else:
            # Weight by trust scores and stance
            weighted_support = sum(c.trustScore * (1 if c.stance == StanceType.SUPPORT else 0) for c in citations)
            weighted_refute = sum(c.trustScore * (1 if c.stance == StanceType.REFUTE else 0) for c in citations)
            weighted_neutral = sum(c.trustScore * (1 if c.stance == StanceType.NEUTRAL else 0) for c in citations)
            
            total_weight = weighted_support + weighted_refute + weighted_neutral
            if total_weight == 0:
                base_score = 50
            else:
                # Score based on weighted evidence (higher = more trustworthy)
                support_ratio = weighted_support / total_weight
                refute_ratio = weighted_refute / total_weight
                
                if refute_ratio > support_ratio:
                    base_score = max(0, 100 - int(refute_ratio * 100))
                else:
                    base_score = min(100, int(support_ratio * 100))
        
        # Adjust based on number of claims (more claims = more complexity = lower confidence)
        claim_penalty = min(20, len(claims) * 5)
        base_score = max(0, base_score - claim_penalty)
        
        # Calculate confidence bands
        citation_count = len(citations)
        if citation_count == 0:
            confidence_range = 0.3
        elif citation_count >= 3:
            confidence_range = 0.1
        else:
            confidence_range = 0.2
        
        mid_confidence = min(0.9, max(0.1, base_score / 100.0))
        low_confidence = max(0.0, mid_confidence - confidence_range)
        high_confidence = min(1.0, mid_confidence + confidence_range)
        
        confidence_bands = ConfidenceBands(
            low=low_confidence,
            mid=mid_confidence,
            high=high_confidence
        )
        
        return base_score, confidence_bands
        
    except Exception as e:
        logger.error(f"Error calculating risk score: {e}")
        return 50, ConfidenceBands(low=0.3, mid=0.5, high=0.7)


@router.post("", response_model=CheckResponse)
async def create_check(
    request: CheckRequest, 
    background_tasks: BackgroundTasks,
    current_user: Optional[dict] = Depends(get_current_user)
):
    """
    Submit content for credibility analysis.
    
    This is the main endpoint for analyzing content (text, URL, or image)
    for potential misinformation using AI-powered detection.
    """
    start_time = time.time()
    
    try:
        # Generate unique ID for this check
        check_id = f"chk_{uuid.uuid4().hex[:12]}"
        
        # Detect language
        detected_language = request.language.value if request.language.value != "auto" else "en"
        if request.language.value == "auto":
            try:
                detected_language = await translation_service.detect_language(request.payload)
            except Exception as e:
                logger.warning(f"Language detection failed: {e}")
                detected_language = "en"
        
        # For URL input type, extract content first
        content_to_analyze = request.payload
        if request.inputType.value == "url":
            try:
                # Extract content from URL (implement URL extraction service)
                content_to_analyze = await extract_url_content(request.payload)
            except Exception as e:
                logger.warning(f"URL extraction failed: {e}")
                content_to_analyze = request.payload
        
        # Translate to English if needed for processing
        processing_content = content_to_analyze
        if detected_language != "en":
            try:
                processing_content = await translation_service.translate_to_english(
                    content_to_analyze, detected_language
                )
            except Exception as e:
                logger.warning(f"Translation failed: {e}")
        
        # Step 1: Extract claims
        claims = await extract_claims_service(processing_content, detected_language)
        
        # Step 2: Retrieve evidence
        citations = await retrieve_evidence_service(claims, detected_language)
        
        # Step 3: Analyze stance
        stance_stats = await analyze_stance_service(claims, citations)
        
        # Step 4: Calculate risk score
        score, confidence_bands = calculate_risk_score(stance_stats, citations, claims)
        
        # Step 5: Generate verdict
        verdict, badge = await generate_verdict_service(score, stance_stats, citations, detected_language)
        
        # Step 6: Get educational content
        learn_cards = await get_learn_cards_service(claims, citations, detected_language)
        
        # Calculate processing time
        latency_ms = int((time.time() - start_time) * 1000)
        
        # Create metadata
        metadata = CheckMetadata(
            language=detected_language,
            contentType=request.inputType,
            createdAt=datetime.utcnow(),
            latencyMs=latency_ms,
            modelVersion="gemini-1.5-flash",
            requestId=check_id
        )
        
        # Create response
        response = CheckResponse(
            id=check_id,
            score=score,
            badge=badge,
            verdict=verdict,
            confidenceBands=confidence_bands,
            claims=claims,
            citations=citations,
            learnCards=learn_cards,
            stanceStats=stance_stats,
            metadata=metadata
        )
        
        # Store result in background
        background_tasks.add_task(
            store_check_result,
            response,
            request,
            current_user
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error processing check request: {e}")
        raise HTTPException(
            status_code=500, 
            detail="Failed to process check request"
        )


@router.get("/{check_id}", response_model=CheckResponse)
async def get_check(check_id: str):
    """
    Retrieve a previously analyzed check result.
    """
    try:
        check_result = await firestore_service.get_check_by_id(check_id)
        if not check_result:
            raise HTTPException(status_code=404, detail="Check not found")
        
        return check_result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving check {check_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve check")


async def store_check_result(
    response: CheckResponse, 
    request: CheckRequest, 
    user: Optional[dict]
):
    """Store check result in Firestore (background task)."""
    try:
        # Hash the payload for privacy
        payload_hash = hashlib.sha256(request.payload.encode()).hexdigest()
        
        # Store in Firestore
        await firestore_service.save_check_result(
            response,
            payload_hash,
            user.get("uid") if user else None
        )
        
        # Store analytics
        await firestore_service.save_check_analytics(response, user)
        
        logger.info(f"Stored check result {response.id}")
        
    except Exception as e:
        logger.error(f"Error storing check result: {e}")


async def extract_url_content(url: str) -> str:
    """Extract content from URL."""
    # Placeholder implementation
    # In a real implementation, this would fetch and extract content from the URL
    try:
        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=10)
            if response.status_code == 200:
                # Simple text extraction (would use BeautifulSoup in real implementation)
                return response.text[:1000]  # Limit content
        return url
    except Exception:
        return url


@router.get("", response_model=list[CheckResponse])
async def list_checks(
    limit: int = 20,
    offset: int = 0,
    user_id: Optional[str] = None,
    current_user: Optional[dict] = Depends(get_current_user)
):
    """
    List recent checks with pagination.
    """
    try:
        # If user_id specified, ensure user can only see their own checks (unless admin)
        if user_id and current_user:
            if user_id != current_user.get("uid") and not current_user.get("admin", False):
                raise HTTPException(status_code=403, detail="Access denied")
        
        checks = await firestore_service.list_checks(limit, offset, user_id)
        return checks
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing checks: {e}")
        raise HTTPException(status_code=500, detail="Failed to list checks")


# Health check endpoint
@router.get("/health", response_model=HealthResponse, include_in_schema=False)
async def health_check():
    """Health check for the checks service."""
    try:
        # Test database connection
        await firestore_service.health_check()
        
        return HealthResponse(
            status="healthy",
            database="connected",
            version=settings.version
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthResponse(
            status="unhealthy",
            database="disconnected",
            version=settings.version
        )
