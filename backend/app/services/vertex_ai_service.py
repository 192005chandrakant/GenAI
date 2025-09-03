"""
Vertex AI Service for Google Vertex AI integration.
Handles Gemini models, embeddings, and grounding capabilities.
"""

import asyncio
import json
import time
from typing import List, Dict, Any, Optional, Tuple
import logging
from datetime import datetime

import vertexai
from vertexai.generative_models import GenerativeModel, Part
from vertexai.language_models import TextEmbeddingModel
from google.cloud import aiplatform

from app.core.config import settings
from app.models.schemas import (
    ContentType, VerdictType, Language, Evidence, Citation, 
    SourceCategory, MediaAnalysis, CheckAnalysis
)

logger = logging.getLogger(__name__)


class VertexAIService:
    """Service for interacting with Google Vertex AI."""
    
    def __init__(self):
        """Initialize Vertex AI service."""
        self.project_id = settings.GOOGLE_CLOUD_PROJECT
        self.location = settings.VERTEX_AI_LOCATION
        
        # Initialize Vertex AI
        vertexai.init(project=self.project_id, location=self.location)
        
        # Initialize models
        self.gemini_flash = GenerativeModel(settings.VERTEX_AI_MODEL_GEMINI_FLASH)
        self.gemini_pro = GenerativeModel(settings.VERTEX_AI_MODEL_GEMINI_PRO)
        self.embedding_model = TextEmbeddingModel.from_pretrained(settings.VERTEX_AI_MODEL_EMBEDDING)
        
        # Model configuration
        self.default_model = settings.AI_MODEL_DEFAULT
        self.escalation_threshold = settings.AI_MODEL_ESCALATION_THRESHOLD
        self.max_tokens = settings.AI_MODEL_MAX_TOKENS
        self.temperature = settings.AI_MODEL_TEMPERATURE
        
        logger.info(f"Vertex AI Service initialized for project {self.project_id}")
    
    async def analyze_text_content(
        self, 
        content: str, 
        language: Language = Language.ENGLISH,
        user_id: Optional[str] = None
    ) -> CheckAnalysis:
        """
        Analyze text content for misinformation detection.
        
        Args:
            content: Text content to analyze
            language: Content language
            user_id: Optional user ID for tracking
            
        Returns:
            CheckAnalysis object with results
        """
        start_time = time.time()
        
        try:
            # Step 1: Extract claims and determine complexity
            claims_result = await self._extract_claims(content, language)
            complexity_score = claims_result.get("complexity_score", 0.5)
            
            # Step 2: Choose model based on complexity
            model_to_use = self._select_model(complexity_score)
            
            # Step 3: Perform comprehensive analysis
            analysis_result = await self._analyze_content_with_model(
                content, claims_result["claims"], language, model_to_use
            )
            
            # Step 4: Generate embeddings for similarity search
            embeddings = await self._generate_embeddings(content)
            
            # Step 5: Create CheckAnalysis object
            latency_ms = int((time.time() - start_time) * 1000)
            
            check_analysis = CheckAnalysis(
                id=analysis_result["check_id"],
                claim=claims_result["primary_claim"],
                evidence=analysis_result["evidence"],
                score=analysis_result["score"],
                verdict=analysis_result["verdict"],
                explanations=analysis_result["explanations"],
                citations=analysis_result["citations"],
                metadata={
                    "language": language.value,
                    "content_type": ContentType.TEXT.value,
                    "user_id": user_id,
                    "complexity_score": complexity_score,
                    "embeddings": embeddings
                },
                performance={
                    "latency_ms": latency_ms,
                    "model_used": model_to_use,
                    "confidence": analysis_result["confidence"]
                },
                language=language,
                content_type=ContentType.TEXT,
                user_id=user_id,
                model_used=model_to_use,
                confidence=analysis_result["confidence"],
                latency_ms=latency_ms
            )
            
            logger.info(f"Text analysis completed in {latency_ms}ms using {model_to_use}")
            return check_analysis
            
        except Exception as e:
            logger.error(f"Error in text analysis: {str(e)}")
            raise
    
    async def analyze_image_content(
        self, 
        image_data: bytes,
        image_metadata: Dict[str, Any],
        language: Language = Language.ENGLISH,
        user_id: Optional[str] = None
    ) -> CheckAnalysis:
        """
        Analyze image content for misinformation detection.
        
        Args:
            image_data: Raw image bytes
            image_metadata: Image metadata
            language: Content language
            user_id: Optional user ID for tracking
            
        Returns:
            CheckAnalysis object with results
        """
        start_time = time.time()
        
        try:
            # Step 1: Extract text from image using OCR
            ocr_text = await self._extract_text_from_image(image_data)
            
            # Step 2: Analyze image content with Gemini Pro Vision
            vision_result = await self._analyze_image_with_vision(
                image_data, ocr_text, language
            )
            
            # Step 3: Generate embeddings
            embeddings = await self._generate_embeddings(vision_result["description"])
            
            # Step 4: Create media analysis
            media_analysis = MediaAnalysis(
                metadata=image_metadata,
                content_type=ContentType.IMAGE,
                processing_time_ms=int((time.time() - start_time) * 1000),
                extracted_text=ocr_text,
                visual_elements=vision_result["visual_elements"]
            )
            
            # Step 5: Create CheckAnalysis object
            latency_ms = int((time.time() - start_time) * 1000)
            
            check_analysis = CheckAnalysis(
                id=vision_result["check_id"],
                claim=vision_result["claim"],
                evidence=vision_result["evidence"],
                score=vision_result["score"],
                verdict=vision_result["verdict"],
                explanations=vision_result["explanations"],
                citations=vision_result["citations"],
                metadata={
                    "language": language.value,
                    "content_type": ContentType.IMAGE.value,
                    "user_id": user_id,
                    "embeddings": embeddings
                },
                performance={
                    "latency_ms": latency_ms,
                    "model_used": settings.VERTEX_AI_MODEL_GEMINI_PRO,
                    "confidence": vision_result["confidence"]
                },
                media_analysis=media_analysis,
                language=language,
                content_type=ContentType.IMAGE,
                user_id=user_id,
                model_used=settings.VERTEX_AI_MODEL_GEMINI_PRO,
                confidence=vision_result["confidence"],
                latency_ms=latency_ms
            )
            
            logger.info(f"Image analysis completed in {latency_ms}ms")
            return check_analysis
            
        except Exception as e:
            logger.error(f"Error in image analysis: {str(e)}")
            raise
    
    async def analyze_video_content(
        self,
        video_data: bytes,
        video_metadata: Dict[str, Any],
        language: Language = Language.ENGLISH,
        user_id: Optional[str] = None
    ) -> CheckAnalysis:
        """
        Analyze video content for misinformation detection.
        
        Args:
            video_data: Raw video bytes
            video_metadata: Video metadata
            language: Content language
            user_id: Optional user ID for tracking
            
        Returns:
            CheckAnalysis object with results
        """
        start_time = time.time()
        
        try:
            # Step 1: Extract frames and audio
            frames, audio_text = await self._extract_video_content(video_data)
            
            # Step 2: Analyze frames with vision model
            frame_analysis = await self._analyze_video_frames(frames, language)
            
            # Step 3: Combine audio and visual analysis
            combined_result = await self._combine_video_analysis(
                frame_analysis, audio_text, language
            )
            
            # Step 4: Generate embeddings
            embeddings = await self._generate_embeddings(combined_result["description"])
            
            # Step 5: Create media analysis
            media_analysis = MediaAnalysis(
                metadata=video_metadata,
                content_type=ContentType.VIDEO,
                processing_time_ms=int((time.time() - start_time) * 1000),
                extracted_text=audio_text,
                visual_elements=frame_analysis["visual_elements"]
            )
            
            # Step 6: Create CheckAnalysis object
            latency_ms = int((time.time() - start_time) * 1000)
            
            check_analysis = CheckAnalysis(
                id=combined_result["check_id"],
                claim=combined_result["claim"],
                evidence=combined_result["evidence"],
                score=combined_result["score"],
                verdict=combined_result["verdict"],
                explanations=combined_result["explanations"],
                citations=combined_result["citations"],
                metadata={
                    "language": language.value,
                    "content_type": ContentType.VIDEO.value,
                    "user_id": user_id,
                    "embeddings": embeddings
                },
                performance={
                    "latency_ms": latency_ms,
                    "model_used": settings.VERTEX_AI_MODEL_GEMINI_PRO,
                    "confidence": combined_result["confidence"]
                },
                media_analysis=media_analysis,
                language=language,
                content_type=ContentType.VIDEO,
                user_id=user_id,
                model_used=settings.VERTEX_AI_MODEL_GEMINI_PRO,
                confidence=combined_result["confidence"],
                latency_ms=latency_ms
            )
            
            logger.info(f"Video analysis completed in {latency_ms}ms")
            return check_analysis
            
        except Exception as e:
            logger.error(f"Error in video analysis: {str(e)}")
            raise
    
    async def generate_embeddings(self, text: str) -> List[float]:
        """
        Generate embeddings for text using Vertex AI.
        
        Args:
            text: Text to embed
            
        Returns:
            List of embedding values
        """
        try:
            embeddings = self.embedding_model.get_embeddings([text])
            return embeddings[0].values
        except Exception as e:
            logger.error(f"Error generating embeddings: {str(e)}")
            raise
    
    async def generate_learning_content(
        self, 
        topic: str, 
        difficulty: str,
        language: Language = Language.ENGLISH
    ) -> Dict[str, Any]:
        """
        Generate educational content about misinformation.
        
        Args:
            topic: Learning topic
            difficulty: Content difficulty level
            language: Content language
            
        Returns:
            Generated learning content
        """
        try:
            prompt = self._build_learning_prompt(topic, difficulty, language)
            
            response = await self._generate_response(
                prompt, 
                model=self.gemini_pro,
                max_tokens=self.max_tokens
            )
            
            return self._parse_learning_response(response)
            
        except Exception as e:
            logger.error(f"Error generating learning content: {str(e)}")
            raise
    
    async def generate_quiz_questions(
        self, 
        topic: str, 
        count: int = 5,
        difficulty: str = "intermediate",
        language: Language = Language.ENGLISH
    ) -> List[Dict[str, Any]]:
        """
        Generate quiz questions for learning assessment.
        
        Args:
            topic: Quiz topic
            count: Number of questions
            difficulty: Question difficulty
            language: Question language
            
        Returns:
            List of quiz questions
        """
        try:
            prompt = self._build_quiz_prompt(topic, count, difficulty, language)
            
            response = await self._generate_response(
                prompt, 
                model=self.gemini_pro,
                max_tokens=self.max_tokens
            )
            
            return self._parse_quiz_response(response)
            
        except Exception as e:
            logger.error(f"Error generating quiz questions: {str(e)}")
            raise
    
    # Private helper methods
    
    async def _extract_claims(self, content: str, language: Language) -> Dict[str, Any]:
        """Extract claims from content and determine complexity."""
        prompt = f"""
        Analyze the following content and extract the main claims. Also assess the complexity.
        
        Content: {content}
        Language: {language.value}
        
        Return a JSON object with:
        - "claims": List of extracted claims
        - "primary_claim": The main claim to focus on
        - "complexity_score": Float between 0-1 indicating complexity
        - "key_entities": List of key entities mentioned
        """
        
        response = await self._generate_response(
            prompt, 
            model=self.gemini_flash,
            max_tokens=1024
        )
        
        return self._parse_json_response(response)
    
    async def _analyze_content_with_model(
        self, 
        content: str, 
        claims: List[str], 
        language: Language,
        model_name: str
    ) -> Dict[str, Any]:
        """Analyze content using specified model."""
        model = self.gemini_pro if model_name == "pro" else self.gemini_flash
        
        prompt = self._build_analysis_prompt(content, claims, language)
        
        response = await self._generate_response(
            prompt, 
            model=model,
            max_tokens=self.max_tokens
        )
        
        return self._parse_analysis_response(response)
    
    async def _analyze_image_with_vision(
        self, 
        image_data: bytes, 
        ocr_text: str, 
        language: Language
    ) -> Dict[str, Any]:
        """Analyze image using Gemini Pro Vision."""
        prompt = self._build_image_analysis_prompt(ocr_text, language)
        
        # Create image part
        image_part = Part.from_data(image_data, mime_type="image/jpeg")
        
        response = await self._generate_vision_response(
            prompt, 
            image_part,
            max_tokens=self.max_tokens
        )
        
        return self._parse_analysis_response(response)
    
    async def _extract_text_from_image(self, image_data: bytes) -> str:
        """Extract text from image using OCR."""
        # This would integrate with Tesseract OCR
        # For now, return empty string
        return ""
    
    async def _extract_video_content(self, video_data: bytes) -> Tuple[List[bytes], str]:
        """Extract frames and audio from video."""
        # This would integrate with FFmpeg
        # For now, return empty lists
        return [], ""
    
    async def _analyze_video_frames(self, frames: List[bytes], language: Language) -> Dict[str, Any]:
        """Analyze video frames."""
        # This would analyze multiple frames
        # For now, return empty result
        return {"visual_elements": [], "description": ""}
    
    async def _combine_video_analysis(
        self, 
        frame_analysis: Dict[str, Any], 
        audio_text: str, 
        language: Language
    ) -> Dict[str, Any]:
        """Combine video frame and audio analysis."""
        # This would combine visual and audio analysis
        # For now, return empty result
        return {
            "check_id": "",
            "claim": "",
            "evidence": [],
            "score": 0.0,
            "verdict": VerdictType.UNVERIFIED,
            "explanations": {},
            "citations": [],
            "confidence": 0.0,
            "description": ""
        }
    
    def _select_model(self, complexity_score: float) -> str:
        """Select appropriate model based on complexity."""
        if complexity_score > self.escalation_threshold:
            return "pro"
        return self.default_model
    
    async def _generate_response(
        self, 
        prompt: str, 
        model: GenerativeModel,
        max_tokens: int = None
    ) -> str:
        """Generate response from Vertex AI model."""
        try:
            response = model.generate_content(
                prompt,
                generation_config={
                    "max_output_tokens": max_tokens or self.max_tokens,
                    "temperature": self.temperature
                }
            )
            return response.text
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            raise
    
    async def _generate_vision_response(
        self, 
        prompt: str, 
        image_part: Part,
        max_tokens: int = None
    ) -> str:
        """Generate response from Vertex AI vision model."""
        try:
            response = self.gemini_pro.generate_content(
                [prompt, image_part],
                generation_config={
                    "max_output_tokens": max_tokens or self.max_tokens,
                    "temperature": self.temperature
                }
            )
            return response.text
        except Exception as e:
            logger.error(f"Error generating vision response: {str(e)}")
            raise
    
    def _build_analysis_prompt(self, content: str, claims: List[str], language: Language) -> str:
        """Build prompt for content analysis."""
        return f"""
        Analyze the following content for misinformation detection.
        
        Content: {content}
        Claims: {', '.join(claims)}
        Language: {language.value}
        
        Provide a comprehensive analysis including:
        1. Reliability score (0-100)
        2. Verdict (true/false/misleading/unverified)
        3. Evidence with sources
        4. Detailed explanations
        5. How the detection was made
        6. Confidence level (0-1)
        
        Return the result as a JSON object with the following structure:
        {{
            "check_id": "unique_id",
            "score": 85.5,
            "verdict": "misleading",
            "confidence": 0.92,
            "evidence": [
                {{
                    "claim": "specific claim",
                    "stance": "false",
                    "confidence": 0.95,
                    "sources": [
                        {{
                            "url": "https://example.com",
                            "title": "Source Title",
                            "domain": "example.com",
                            "credibility_score": 95.0,
                            "category": "fact_check",
                            "snippet": "relevant text"
                        }}
                    ],
                    "reasoning": "detailed reasoning",
                    "relevance_score": 0.9
                }}
            ],
            "explanations": {{
                "summary": "brief summary",
                "reasoning": "detailed reasoning",
                "how_detected": "step-by-step detection process"
            }},
            "citations": [
                {{
                    "url": "https://example.com",
                    "title": "Source Title",
                    "domain": "example.com",
                    "credibility_score": 95.0,
                    "category": "fact_check",
                    "snippet": "relevant text"
                }}
            ]
        }}
        """
    
    def _build_image_analysis_prompt(self, ocr_text: str, language: Language) -> str:
        """Build prompt for image analysis."""
        return f"""
        Analyze this image for potential misinformation.
        
        OCR Text: {ocr_text}
        Language: {language.value}
        
        Examine the image for:
        1. Text content and claims
        2. Visual elements that might be manipulated
        3. Context and source credibility
        4. Potential misinformation indicators
        
        Provide the same JSON structure as text analysis.
        """
    
    def _build_learning_prompt(self, topic: str, difficulty: str, language: Language) -> str:
        """Build prompt for learning content generation."""
        return f"""
        Create educational content about misinformation detection.
        
        Topic: {topic}
        Difficulty: {difficulty}
        Language: {language.value}
        
        Include:
        1. Clear explanation of the concept
        2. Real-world examples
        3. Tips for detection
        4. Interactive elements
        5. Key takeaways
        
        Format as structured content with sections.
        """
    
    def _build_quiz_prompt(self, topic: str, count: int, difficulty: str, language: Language) -> str:
        """Build prompt for quiz generation."""
        return f"""
        Create {count} quiz questions about misinformation detection.
        
        Topic: {topic}
        Difficulty: {difficulty}
        Language: {language.value}
        
        Each question should have:
        1. Clear question text
        2. 4 multiple choice options
        3. Correct answer (0-3)
        4. Explanation for the answer
        5. Difficulty level
        
        Return as JSON array of questions.
        """
    
    def _parse_analysis_response(self, response: str) -> Dict[str, Any]:
        """Parse AI analysis response."""
        try:
            # Extract JSON from response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start == -1 or json_end == 0:
                raise ValueError("No JSON found in response")
            
            json_str = response[json_start:json_end]
            result = json.loads(json_str)
            
            # Validate required fields
            required_fields = ["check_id", "score", "verdict", "confidence", "evidence", "explanations", "citations"]
            for field in required_fields:
                if field not in result:
                    raise ValueError(f"Missing required field: {field}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error parsing analysis response: {str(e)}")
            # Return default response
            return {
                "check_id": f"check_{int(time.time())}",
                "score": 50.0,
                "verdict": VerdictType.UNVERIFIED.value,
                "confidence": 0.5,
                "evidence": [],
                "explanations": {
                    "summary": "Unable to analyze content",
                    "reasoning": "Analysis failed",
                    "how_detected": "Manual review required"
                },
                "citations": []
            }
    
    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        """Parse JSON response from AI."""
        try:
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start == -1 or json_end == 0:
                raise ValueError("No JSON found in response")
            
            json_str = response[json_start:json_end]
            return json.loads(json_str)
            
        except Exception as e:
            logger.error(f"Error parsing JSON response: {str(e)}")
            return {}
    
    def _parse_learning_response(self, response: str) -> Dict[str, Any]:
        """Parse learning content response."""
        # This would parse structured learning content
        return {
            "title": "Learning Content",
            "content": response,
            "sections": [],
            "key_points": []
        }
    
    def _parse_quiz_response(self, response: str) -> List[Dict[str, Any]]:
        """Parse quiz questions response."""
        try:
            questions = self._parse_json_response(response)
            if isinstance(questions, list):
                return questions
            return []
        except Exception as e:
            logger.error(f"Error parsing quiz response: {str(e)}")
            return []
