"""
Content analysis endpoints for misinformation detection.
"""
import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse

from app.models.schemas import (
    ContentAnalysisRequest,
    ContentAnalysisResponse,
    ContentType,
    Language,
    BaseResponse,
    ErrorResponse
)
from app.services.gemini_service import gemini_service
from app.services.translation_service import translation_service
from app.services.firestore_service import firestore_service

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/analyze", response_model=ContentAnalysisResponse)
async def analyze_content(request: ContentAnalysisRequest):
    """
    Analyze text content or links for misinformation.
    
    This endpoint analyzes text content or URLs for potential misinformation
    using Google Gemini AI and provides detailed explanations.
    """
    try:
        # Detect language if auto-detection is requested
        detected_language = request.language.value
        if request.language == Language.AUTO:
            detected_language = await translation_service.detect_language(request.content)
            if not detected_language:
                detected_language = "en"  # Default to English
        
        # Translate content to English if it's not already in English
        translated_content = None
        if detected_language != "en":
            translated_content = await translation_service.translate_to_english(
                request.content, detected_language
            )
        
        # Analyze content using Gemini AI
        analysis_content = translated_content if translated_content else request.content
        analysis_result = await gemini_service.analyze_text_content(
            analysis_content, request.content_type, detected_language
        )
        
        # Update the analysis result with translation info
        analysis_result.detected_language = detected_language
        analysis_result.translated_content = translated_content
        
        # Save analysis result to database
        await firestore_service.save_content_analysis(analysis_result)
        
        # Award points to user if provided
        if request.user_id:
            points_to_award = 10  # Base points for analysis
            await firestore_service.add_points(
                request.user_id, 
                points_to_award, 
                "Content analysis completed",
                analysis_result.content_id
            )
        
        return analysis_result
        
    except Exception as e:
        logger.error(f"Error analyzing content: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to analyze content")


@router.post("/analyze-image", response_model=ContentAnalysisResponse)
async def analyze_image(
    file: UploadFile = File(...),
    additional_context: Optional[str] = Form(None),
    user_id: Optional[str] = Form(None)
):
    """
    Analyze uploaded image for misinformation.
    
    This endpoint analyzes images for potential misinformation using
    Google Gemini Vision AI.
    """
    try:
        # Validate file type
        if not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Read image data
        image_data = await file.read()
        
        # Analyze image using Gemini Vision
        analysis_result = await gemini_service.analyze_image_content(
            image_data, additional_context
        )
        
        # Save analysis result to database
        await firestore_service.save_content_analysis(analysis_result)
        
        # Award points to user if provided
        if user_id:
            points_to_award = 15  # More points for image analysis
            await firestore_service.add_points(
                user_id, 
                points_to_award, 
                "Image analysis completed",
                analysis_result.content_id
            )
        
        return analysis_result
        
    except Exception as e:
        logger.error(f"Error analyzing image: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to analyze image")


@router.get("/analysis/{content_id}", response_model=ContentAnalysisResponse)
async def get_analysis_result(content_id: str):
    """
    Get analysis result by content ID.
    
    Retrieve a previously performed content analysis by its ID.
    """
    try:
        analysis_result = await firestore_service.get_content_analysis(content_id)
        if not analysis_result:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        return analysis_result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving analysis: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve analysis")


@router.post("/translate", response_model=dict)
async def translate_content(
    text: str = Form(...),
    target_language: Language = Form(...),
    source_language: Optional[str] = Form(None)
):
    """
    Translate content to target language.
    
    Translate text content to the specified target language using
    Google Cloud Translation API.
    """
    try:
        translated_text = await translation_service.translate_text(
            text, target_language, source_language
        )
        
        if not translated_text:
            raise HTTPException(status_code=400, detail="Translation failed")
        
        return {
            "original_text": text,
            "translated_text": translated_text,
            "target_language": target_language.value,
            "source_language": source_language or "auto-detected"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error translating content: {str(e)}")
        raise HTTPException(status_code=500, detail="Translation failed")


@router.get("/languages", response_model=dict)
async def get_supported_languages():
    """
    Get list of supported languages for translation.
    
    Returns a list of languages supported by the Google Cloud Translation API.
    """
    try:
        languages = await translation_service.get_supported_languages()
        return {
            "languages": languages,
            "count": len(languages)
        }
        
    except Exception as e:
        logger.error(f"Error getting supported languages: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get supported languages")


@router.post("/batch-analyze", response_model=list[ContentAnalysisResponse])
async def batch_analyze_content(requests: list[ContentAnalysisRequest]):
    """
    Analyze multiple content items in batch.
    
    This endpoint analyzes multiple text content items for misinformation
    in a single request for improved efficiency.
    """
    try:
        results = []
        
        for request in requests:
            try:
                # Detect language
                detected_language = request.language.value
                if request.language == Language.AUTO:
                    detected_language = await translation_service.detect_language(request.content)
                    if not detected_language:
                        detected_language = "en"
                
                # Translate if needed
                translated_content = None
                if detected_language != "en":
                    translated_content = await translation_service.translate_to_english(
                        request.content, detected_language
                    )
                
                # Analyze content
                analysis_content = translated_content if translated_content else request.content
                analysis_result = await gemini_service.analyze_text_content(
                    analysis_content, request.content_type, detected_language
                )
                
                # Update with translation info
                analysis_result.detected_language = detected_language
                analysis_result.translated_content = translated_content
                
                # Save to database
                await firestore_service.save_content_analysis(analysis_result)
                
                results.append(analysis_result)
                
            except Exception as e:
                logger.error(f"Error in batch analysis item: {str(e)}")
                # Continue with other items
                continue
        
        return results
        
    except Exception as e:
        logger.error(f"Error in batch analysis: {str(e)}")
        raise HTTPException(status_code=500, detail="Batch analysis failed")
