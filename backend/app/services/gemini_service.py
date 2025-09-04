"""
Google Gemini AI service for content analysis and misinformation detection.
"""
import time
import logging
from typing import List, Dict, Any, Optional
import google.generativeai as genai
from PIL import Image
import io

from app.core.config import settings
from app.models.schemas import (
    ContentType,
    MisinformationLevel,
    DetectionExplanation,
    SourceInfo,
    ContentAnalysisResponse,
)

logger = logging.getLogger(__name__)


class GeminiService:
    """Service for interacting with Google Gemini AI."""
    
    def __init__(self):
        """Initialize Gemini service with API key."""
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.text_model = genai.GenerativeModel(settings.GEMINI_MODEL)
        self.vision_model = genai.GenerativeModel(settings.GEMINI_VISION_MODEL)
        
    async def analyze_text_content(
        self, 
        content: str, 
        content_type: ContentType,
        language: str = "en"
    ) -> ContentAnalysisResponse:
        """
        Analyze text content for misinformation using Gemini AI.
        
        Args:
            content: The text content to analyze
            content_type: Type of content (text, link)
            language: Language of the content
            
        Returns:
            ContentAnalysisResponse with analysis results
        """
        start_time = time.time()
        
        try:
            # Prepare the prompt for analysis
            prompt = self._build_analysis_prompt(content, content_type, language)
            
            # Generate response from Gemini
            response = await self._generate_response(prompt)
            
            # Parse the response
            analysis_result = self._parse_analysis_response(response)
            
            # Calculate processing time
            processing_time = time.time() - start_time
            
            # Generate content ID
            content_id = f"content_{int(start_time)}"
            
            return ContentAnalysisResponse(
                content_id=content_id,
                original_content=content,
                detected_language=language,
                misinformation_level=analysis_result["misinformation_level"],
                reliability_score=analysis_result["reliability_score"],
                explanation=analysis_result["explanation"],
                sources=analysis_result.get("sources", []),
                processing_time=processing_time
            )
            
        except Exception as e:
            logger.error(f"Error analyzing text content: {str(e)}")
            raise
    
    async def analyze_image_content(
        self, 
        image_data: bytes,
        additional_context: Optional[str] = None
    ) -> ContentAnalysisResponse:
        """
        Analyze image content for misinformation using Gemini Vision.
        
        Args:
            image_data: Raw image bytes
            additional_context: Additional text context if available
            
        Returns:
            ContentAnalysisResponse with analysis results
        """
        start_time = time.time()
        
        try:
            # Convert bytes to PIL Image
            image = Image.open(io.BytesIO(image_data))
            
            # Prepare the prompt for image analysis
            prompt = self._build_image_analysis_prompt(additional_context)
            
            # Generate response from Gemini Vision
            response = await self._generate_vision_response(prompt, image)
            
            # Parse the response
            analysis_result = self._parse_analysis_response(response)
            
            # Calculate processing time
            processing_time = time.time() - start_time
            
            # Generate content ID
            content_id = f"image_{int(start_time)}"
            
            return ContentAnalysisResponse(
                content_id=content_id,
                original_content="[Image Content]",
                detected_language="en",  # Default for images
                misinformation_level=analysis_result["misinformation_level"],
                reliability_score=analysis_result["reliability_score"],
                explanation=analysis_result["explanation"],
                sources=analysis_result.get("sources", []),
                processing_time=processing_time
            )
            
        except Exception as e:
            logger.error(f"Error analyzing image content: {str(e)}")
            raise
    
    def _build_analysis_prompt(
        self, 
        content: str, 
        content_type: ContentType,
        language: str
    ) -> str:
        """Build the analysis prompt for Gemini AI."""
        
        base_prompt = f"""
        You are an expert fact-checker and misinformation detection specialist. 
        Analyze the following {content_type.value} content for potential misinformation.
        
        Content Language: {language}
        Content Type: {content_type.value}
        
        Content to analyze:
        "{content}"
        
        Please provide a comprehensive analysis in the following JSON format:
        {{
            "misinformation_level": "low|medium|high|critical",
            "reliability_score": 0.0-1.0,
            "explanation": {{
                "reasoning": "Detailed explanation of why this content was flagged",
                "key_indicators": ["indicator1", "indicator2", "indicator3"],
                "confidence_score": 0.0-1.0,
                "suggested_actions": ["action1", "action2", "action3"]
            }},
            "sources": [
                {{
                    "title": "Source title",
                    "url": "https://source-url.com",
                    "description": "Brief description",
                    "reliability_score": 0.0-1.0
                }}
            ]
        }}
        
        Guidelines for analysis:
        1. Check for sensationalist language, unverified claims, or emotional manipulation
        2. Look for missing context, cherry-picked facts, or logical fallacies
        3. Identify potential bias, conspiracy theories, or pseudoscience
        4. Consider the source credibility and fact-checking history
        5. Provide specific, actionable feedback for users
        
        Be thorough but fair in your analysis. If the content appears legitimate, 
        indicate a low misinformation level with high reliability score.
        """
        
        return base_prompt
    
    def _build_image_analysis_prompt(self, additional_context: Optional[str] = None) -> str:
        """Build the image analysis prompt for Gemini Vision."""
        
        context_part = f"\nAdditional Context: {additional_context}" if additional_context else ""
        
        prompt = f"""
        You are an expert fact-checker analyzing an image for potential misinformation.
        {context_part}
        
        Please analyze this image and provide a comprehensive assessment in the following JSON format:
        {{
            "misinformation_level": "low|medium|high|critical",
            "reliability_score": 0.0-1.0,
            "explanation": {{
                "reasoning": "Detailed explanation of what you see and why it was flagged",
                "key_indicators": ["indicator1", "indicator2", "indicator3"],
                "confidence_score": 0.0-1.0,
                "suggested_actions": ["action1", "action2", "action3"]
            }},
            "sources": [
                {{
                    "title": "Source title",
                    "url": "https://source-url.com",
                    "description": "Brief description",
                    "reliability_score": 0.0-1.0
                }}
            ]
        }}
        
        Consider:
        1. Visual manipulation, deepfakes, or edited images
        2. Misleading captions or context
        3. Outdated or misattributed images
        4. Emotional manipulation through imagery
        5. Missing context or selective framing
        
        Describe what you see in the image and explain your reasoning clearly.
        """
        
        return prompt
    
    async def _generate_response(self, prompt: str) -> str:
        """Generate response from Gemini text model."""
        try:
            response = self.text_model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Error generating Gemini response: {str(e)}")
            raise
    
    async def _generate_vision_response(self, prompt: str, image: Image.Image) -> str:
        """Generate response from Gemini vision model."""
        try:
            response = self.vision_model.generate_content([prompt, image])
            return response.text
        except Exception as e:
            logger.error(f"Error generating Gemini vision response: {str(e)}")
            raise
    
    def _parse_analysis_response(self, response: str) -> Dict[str, Any]:
        """Parse the Gemini response into structured data."""
        try:
            import json
            
            # Extract JSON from response (handle cases where response includes extra text)
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            
            if start_idx == -1 or end_idx == 0:
                raise ValueError("No JSON found in response")
            
            json_str = response[start_idx:end_idx]
            data = json.loads(json_str)
            
            # Validate and structure the response
            misinformation_level = MisinformationLevel(data.get("misinformation_level", "low"))
            reliability_score = float(data.get("reliability_score", 0.5))
            
            explanation_data = data.get("explanation", {})
            explanation = DetectionExplanation(
                reasoning=explanation_data.get("reasoning", "No reasoning provided"),
                key_indicators=explanation_data.get("key_indicators", []),
                confidence_score=float(explanation_data.get("confidence_score", 0.5)),
                suggested_actions=explanation_data.get("suggested_actions", [])
            )
            
            sources = []
            for source_data in data.get("sources", []):
                source = SourceInfo(
                    title=source_data.get("title", ""),
                    url=source_data.get("url", "https://example.com"),
                    description=source_data.get("description", ""),
                    reliability_score=float(source_data.get("reliability_score", 0.5))
                )
                sources.append(source)
            
            return {
                "misinformation_level": misinformation_level,
                "reliability_score": reliability_score,
                "explanation": explanation,
                "sources": sources
            }
            
        except Exception as e:
            logger.error(f"Error parsing analysis response: {str(e)}")
            # Return default response if parsing fails
            return {
                "misinformation_level": MisinformationLevel.LOW,
                "reliability_score": 0.5,
                "explanation": DetectionExplanation(
                    reasoning="Unable to parse AI response",
                    key_indicators=["Analysis failed"],
                    confidence_score=0.0,
                    suggested_actions=["Please try again or contact support"]
                ),
                "sources": []
            }
    
    async def generate_learning_content(self, topic: str) -> str:
        """Generate educational content about misinformation detection."""
        prompt = f"""
        Create an educational module about "{topic}" related to misinformation detection.
        Make it engaging, informative, and suitable for general audiences.
        Include practical tips and examples.
        """
        
        try:
            response = await self._generate_response(prompt)
            return response
        except Exception as e:
            logger.error(f"Error generating learning content: {str(e)}")
            return f"Unable to generate content about {topic}. Please try again later."
    
    async def generate_quiz_questions(self, topic: str, num_questions: int = 5) -> List[Dict[str, Any]]:
        """Generate quiz questions for learning modules."""
        prompt = f"""
        Generate {num_questions} multiple-choice questions about "{topic}" 
        related to misinformation detection. Format as JSON:
        {{
            "questions": [
                {{
                    "question": "Question text",
                    "options": ["A", "B", "C", "D"],
                    "correct_answer": 0,
                    "explanation": "Why this is correct"
                }}
            ]
        }}
        """
        
        try:
            response = await self._generate_response(prompt)
            # Parse response and extract questions
            import json
            data = json.loads(response)
            return data.get("questions", [])
        except Exception as e:
            logger.error(f"Error generating quiz questions: {str(e)}")
            return []


# Global instance
gemini_service = GeminiService()
