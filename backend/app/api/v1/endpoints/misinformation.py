"""
Enhanced misinformation detection endpoints using advanced Gemini AI capabilities.
Implements structured claim extraction, evidence-grounded retrieval, and stance analysis.
"""
import logging
import hashlib
import time
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse

from app.models.misinformation_schemas import (
    MisinformationAnalysisRequest,
    MisinformationAnalysisResponse,
    BatchAnalysisRequest,
    BatchAnalysisResponse,
    ClaimExtraction,
    EvidenceCitation,
    StanceAnalysis,
    DetailedAnalysisLog,
    ProcessingModel
)
from app.core.config import settings
from app.services.gemini_service import enhanced_gemini_service
from app.services.firestore_service import firestore_service
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


@router.post("/analyze", response_model=MisinformationAnalysisResponse)
async def analyze_misinformation_enhanced(
    request: MisinformationAnalysisRequest,
    background_tasks: BackgroundTasks,
    current_user: Optional[dict] = Depends(get_current_user)
):
    """
    Enhanced misinformation analysis with structured claim extraction,
    evidence-grounded retrieval, and stance analysis using Gemini AI.
    
    This endpoint provides comprehensive analysis including:
    - Language detection and claim extraction
    - Evidence retrieval from multiple sources
    - Stance analysis with confidence scoring
    - Credibility scoring with traffic light badges
    - Educational learn cards for digital literacy
    - Manipulation technique identification
    """
    start_time = time.time()
    
    try:
        logger.info(f"🚀 Starting enhanced misinformation analysis for content: {request.content[:100]}...")
        
        # Perform enhanced analysis
        analysis_result = await enhanced_gemini_service.analyze_misinformation_enhanced(request)
        
        logger.info(f"✅ Enhanced analysis completed in {analysis_result.processing_time:.2f}s")
        
        # Store result in background for analytics and caching
        background_tasks.add_task(
            store_enhanced_analysis_result,
            analysis_result,
            request,
            current_user
        )
        
        return analysis_result
        
    except Exception as e:
        logger.error(f"❌ Enhanced misinformation analysis failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to analyze content: {str(e)}"
        )


@router.post("/analyze/batch", response_model=BatchAnalysisResponse)
async def analyze_batch_content(
    request: BatchAnalysisRequest,
    background_tasks: BackgroundTasks,
    current_user: Optional[dict] = Depends(get_current_user)
):
    """
    Batch analysis of multiple content items for misinformation detection.
    Useful for processing multiple claims or content pieces simultaneously.
    """
    start_time = time.time()
    
    try:
        batch_id = f"batch_{uuid.uuid4().hex[:12]}"
        
        logger.info(f"🚀 Starting batch analysis {batch_id} for {len(request.contents)} items")
        
        results = []
        completed_items = 0
        failed_items = 0
        
        for i, content in enumerate(request.contents):
            try:
                # Create individual analysis request
                content_type = request.content_types[i] if request.content_types and i < len(request.content_types) else "text"
                
                analysis_request = MisinformationAnalysisRequest(
                    content=content,
                    content_type=content_type,
                    context={"batch_id": batch_id, "item_index": i}
                )
                
                # Perform analysis
                result = await enhanced_gemini_service.analyze_misinformation_enhanced(analysis_request)
                results.append(result)
                completed_items += 1
                
                logger.info(f"✅ Completed batch item {i+1}/{len(request.contents)}")
                
            except Exception as e:
                logger.error(f"❌ Failed to analyze batch item {i+1}: {str(e)}")
                failed_items += 1
        
        batch_response = BatchAnalysisResponse(
            batch_id=batch_id,
            total_items=len(request.contents),
            completed_items=completed_items,
            failed_items=failed_items,
            results=results,
            status="completed" if failed_items == 0 else "partial",
            started_at=datetime.fromtimestamp(start_time),
            completed_at=datetime.now()
        )
        
        # Store batch results in background
        background_tasks.add_task(
            store_batch_analysis_result,
            batch_response,
            request,
            current_user
        )
        
        logger.info(f"✅ Batch analysis {batch_id} completed: {completed_items} success, {failed_items} failed")
        
        return batch_response
        
    except Exception as e:
        logger.error(f"❌ Batch analysis failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process batch analysis: {str(e)}"
        )


@router.get("/analysis/{content_id}", response_model=MisinformationAnalysisResponse)
async def get_analysis_result(
    content_id: str,
    current_user: Optional[dict] = Depends(get_current_user)
):
    """
    Retrieve a previously completed misinformation analysis by content ID.
    """
    try:
        # Try to retrieve from cache or database
        analysis_result = await retrieve_analysis_from_storage(content_id)
        
        if not analysis_result:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        return analysis_result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error retrieving analysis {content_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve analysis")


@router.get("/claims/extract")
async def extract_claims_endpoint(
    content: str,
    language: str = "auto",
    current_user: Optional[dict] = Depends(get_current_user)
):
    """
    Extract claims from content without full analysis.
    Useful for understanding what claims would be fact-checked.
    """
    try:
        # Detect language if auto
        detected_language = language
        if language == "auto":
            detected_language = await enhanced_gemini_service.detect_language(content)
        
        # Extract claims
        claims = await enhanced_gemini_service.extract_claims(content, detected_language)
        
        return {
            "success": True,
            "detected_language": detected_language.value,
            "claims": [
                {
                    "claim_text": claim.claim_text,
                    "who": claim.who,
                    "what": claim.what,
                    "where": claim.where,
                    "when": claim.when,
                    "confidence": claim.confidence
                }
                for claim in claims
            ],
            "total_claims": len(claims)
        }
        
    except Exception as e:
        logger.error(f"❌ Claim extraction failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to extract claims")


@router.get("/evidence/search")
async def search_evidence_endpoint(
    claims: List[str],
    language: str = "en",
    max_results: int = 5,
    current_user: Optional[dict] = Depends(get_current_user)
):
    """
    Search for evidence related to specific claims.
    Returns citations from multiple sources without full analysis.
    """
    try:
        # Convert string claims to ClaimExtraction objects
        claim_objects = [
            ClaimExtraction(
                claim_text=claim,
                what=claim,
                confidence=1.0
            )
            for claim in claims
        ]
        
        # Search for evidence
        evidence_result = await enhanced_gemini_service.retrieve_evidence(claim_objects)
        
        # Limit results
        limited_citations = evidence_result.citations_found[:max_results]
        
        return {
            "success": True,
            "query": evidence_result.query,
            "sources_searched": evidence_result.sources_searched,
            "citations": [
                {
                    "title": citation.title,
                    "url": str(citation.url),
                    "snippet": citation.snippet,
                    "date": citation.date.isoformat() if citation.date else None,
                    "source_type": citation.source_type,
                    "relevance_score": citation.relevance_score,
                    "credibility_weight": citation.credibility_weight
                }
                for citation in limited_citations
            ],
            "total_results": evidence_result.total_results,
            "search_time": evidence_result.search_time
        }
        
    except Exception as e:
        logger.error(f"❌ Evidence search failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to search evidence")


@router.get("/stats/cache")
async def get_cache_stats(current_user: Optional[dict] = Depends(get_current_user)):
    """
    Get cache statistics for monitoring performance.
    Admin endpoint for observability.
    """
    try:
        # Check if user is admin
        if not current_user or not current_user.get("admin", False):
            raise HTTPException(status_code=403, detail="Admin access required")
        
        cache_stats = {
            "total_entries": len(enhanced_gemini_service.analysis_cache),
            "cache_ttl_hours": enhanced_gemini_service.cache_ttl_hours,
            "entries": []
        }
        
        for content_hash, cache_entry in enhanced_gemini_service.analysis_cache.items():
            cache_stats["entries"].append({
                "content_hash": content_hash[:16] + "...",
                "created_at": cache_entry.created_at.isoformat(),
                "access_count": cache_entry.access_count,
                "last_accessed": cache_entry.last_accessed.isoformat(),
                "score": cache_entry.result.score,
                "badge": cache_entry.result.badge.value
            })
        
        return cache_stats
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error retrieving cache stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve cache statistics")


@router.post("/cache/clear")
async def clear_cache(current_user: Optional[dict] = Depends(get_current_user)):
    """
    Clear the analysis cache.
    Admin endpoint for cache management.
    """
    try:
        # Check if user is admin
        if not current_user or not current_user.get("admin", False):
            raise HTTPException(status_code=403, detail="Admin access required")
        
        entries_cleared = len(enhanced_gemini_service.analysis_cache)
        enhanced_gemini_service.analysis_cache.clear()
        
        logger.info(f"🧹 Admin {current_user.get('uid')} cleared {entries_cleared} cache entries")
        
        return {
            "success": True,
            "entries_cleared": entries_cleared,
            "message": "Cache cleared successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error clearing cache: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to clear cache")


async def store_enhanced_analysis_result(
    analysis_result: MisinformationAnalysisResponse,
    request: MisinformationAnalysisRequest,
    user: Optional[dict]
):
    """Store enhanced analysis result in Firestore (background task)."""
    try:
        # Hash the content for privacy
        content_hash = hashlib.sha256(request.content.encode()).hexdigest()
        
        # Prepare data for storage
        storage_data = {
            "content_id": analysis_result.content_id,
            "content_hash": content_hash,
            "user_id": user.get("uid") if user else None,
            "language": analysis_result.language.value,
            "processing_model": analysis_result.processing_model.value,
            "score": analysis_result.score,
            "badge": analysis_result.badge.value,
            "verdict": analysis_result.verdict,
            "claims_count": len(analysis_result.claims),
            "citations_count": len(analysis_result.citations),
            "manipulation_techniques": [tech.value for tech in analysis_result.manipulation_techniques],
            "processing_time": analysis_result.processing_time,
            "model_escalated": analysis_result.model_escalated,
            "cache_hit": analysis_result.cache_hit,
            "created_at": analysis_result.created_at,
            "request_context": request.context
        }
        
        # Store in Firestore
        await firestore_service.save_enhanced_analysis(storage_data)
        
        logger.info(f"📦 Stored enhanced analysis {analysis_result.content_id}")
        
    except Exception as e:
        logger.error(f"❌ Error storing enhanced analysis result: {str(e)}")


async def store_batch_analysis_result(
    batch_response: BatchAnalysisResponse,
    request: BatchAnalysisRequest,
    user: Optional[dict]
):
    """Store batch analysis result in Firestore (background task)."""
    try:
        # Prepare batch data for storage
        batch_data = {
            "batch_id": batch_response.batch_id,
            "user_id": user.get("uid") if user else None,
            "total_items": batch_response.total_items,
            "completed_items": batch_response.completed_items,
            "failed_items": batch_response.failed_items,
            "status": batch_response.status,
            "started_at": batch_response.started_at,
            "completed_at": batch_response.completed_at,
            "priority": request.priority,
            "callback_url": str(request.callback_url) if request.callback_url else None
        }
        
        # Store batch metadata
        await firestore_service.save_batch_analysis(batch_data)
        
        # Store individual results
        for result in batch_response.results:
            await store_enhanced_analysis_result(
                result,
                MisinformationAnalysisRequest(content="batch_item", context={"batch_id": batch_response.batch_id}),
                user
            )
        
        logger.info(f"📦 Stored batch analysis {batch_response.batch_id}")
        
    except Exception as e:
        logger.error(f"❌ Error storing batch analysis result: {str(e)}")


async def retrieve_analysis_from_storage(content_id: str) -> Optional[MisinformationAnalysisResponse]:
    """Retrieve analysis result from storage."""
    try:
        # Try to retrieve from Firestore
        stored_data = await firestore_service.get_enhanced_analysis(content_id)
        
        if not stored_data:
            return None
        
        # Convert stored data back to response model
        # This would require implementing the conversion logic
        # For now, return None to indicate not found
        return None
        
    except Exception as e:
        logger.error(f"❌ Error retrieving analysis from storage: {str(e)}")
        return None


@router.get("/health")
async def health_check():
    """Health check for the enhanced misinformation detection service."""
    try:
        # Test service components
        service_status = {
            "gemini_service": "healthy" if enhanced_gemini_service.flash_model else "unhealthy",
            "cache_entries": len(enhanced_gemini_service.analysis_cache),
            "timestamp": datetime.now().isoformat()
        }
        
        return {
            "status": "healthy",
            "service": "enhanced_misinformation_detection",
            "version": "1.0.0",
            "components": service_status
        }
        
    except Exception as e:
        logger.error(f"❌ Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }