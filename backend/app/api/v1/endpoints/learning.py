"""
Learning and educational content endpoints.
"""
import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException
from app.models.dto import LearnCard, BaseResponse
from app.services.firestore_service import firestore_service
from app.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/cards", response_model=List[LearnCard])
async def get_learn_cards(
    technique: Optional[str] = None,
    difficulty: Optional[str] = None,
    language: str = "en",
    limit: int = 10
):
    """Get educational learn cards."""
    try:
        if settings.use_mocks:
            return [
                LearnCard(
                    technique="Cherry picking",
                    explanation="Selectively presenting facts that support a position",
                    example="Showing only positive reviews while hiding negative ones",
                    difficulty="beginner"
                ),
                LearnCard(
                    technique="Strawman argument",
                    explanation="Misrepresenting someone's argument to make it easier to attack",
                    example="Person A: We should have some restrictions. Person B: Person A wants to ban everything!",
                    difficulty="intermediate"
                )
            ]
        
        cards = await firestore_service.get_learn_cards(
            technique=technique,
            difficulty=difficulty,
            language=language,
            limit=limit
        )
        return cards
        
    except Exception as e:
        logger.error(f"Error getting learn cards: {e}")
        raise HTTPException(status_code=500, detail="Failed to get learn cards")


@router.get("/techniques")
async def get_manipulation_techniques():
    """Get list of manipulation techniques."""
    try:
        if settings.use_mocks:
            return {
                "techniques": [
                    "Cherry picking",
                    "Strawman argument", 
                    "False dichotomy",
                    "Ad hominem",
                    "Appeal to emotion",
                    "Bandwagon fallacy"
                ]
            }
        
        techniques = await firestore_service.get_manipulation_techniques()
        return {"techniques": techniques}
        
    except Exception as e:
        logger.error(f"Error getting techniques: {e}")
        raise HTTPException(status_code=500, detail="Failed to get techniques")
