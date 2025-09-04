"""
Gamification endpoints for user engagement and rewards.
"""
import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends
from app.models.dto import BaseResponse
from app.models.gamification_schemas import (
    Achievement, Badge, Leaderboard, UserStats, Challenge,
    PointsTransaction, LevelInfo
)
from app.auth.firebase import get_current_user
from app.services.firestore_service import firestore_service
from app.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/leaderboard", response_model=Leaderboard)
async def get_leaderboard(
    period: str = "all",  # all, weekly, monthly
    limit: int = 100,
    category: Optional[str] = None  # points, accuracy, streak
):
    """Get user leaderboard with different time periods and categories."""
    try:
        if settings.use_mocks:
            return Leaderboard(
                period=period,
                category=category or "points",
                entries=[
                    {
                        "rank": 1,
                        "user_id": "user_001",
                        "display_name": "TopChecker",
                        "score": 2450,
                        "avatar_url": None,
                        "badges": ["fact_master", "streak_champion"]
                    },
                    {
                        "rank": 2,
                        "user_id": "user_002", 
                        "display_name": "TruthSeeker",
                        "score": 2100,
                        "avatar_url": None,
                        "badges": ["accuracy_pro"]
                    }
                ],
                total_participants=156,
                last_updated="2025-09-04T10:00:00Z"
            )
        
        leaderboard = await firestore_service.get_leaderboard(period, limit, category)
        return leaderboard
        
    except Exception as e:
        logger.error(f"Error getting leaderboard: {e}")
        raise HTTPException(status_code=500, detail="Failed to get leaderboard")


@router.get("/achievements", response_model=List[Achievement])
async def get_achievements(
    category: Optional[str] = None,
    earned_only: bool = False,
    current_user: dict = Depends(get_current_user)
):
    """Get available achievements with progress tracking."""
    try:
        user_id = current_user.get("uid") if current_user else None
        
        if settings.use_mocks:
            return [
                Achievement(
                    id="first_check",
                    title="First Check",
                    description="Complete your first fact check",
                    category="milestone",
                    icon_url="/icons/first-check.png",
                    points_reward=50,
                    badge_id="newcomer",
                    requirements={"checks_completed": 1},
                    progress={"checks_completed": 1} if user_id else {"checks_completed": 0},
                    earned=True if user_id else False,
                    earned_at="2025-09-04T09:00:00Z" if user_id else None
                ),
                Achievement(
                    id="accuracy_expert",
                    title="Accuracy Expert", 
                    description="Maintain 90%+ accuracy over 50 checks",
                    category="skill",
                    icon_url="/icons/accuracy.png",
                    points_reward=200,
                    badge_id="accuracy_pro",
                    requirements={"accuracy_rate": 90, "min_checks": 50},
                    progress={"accuracy_rate": 85, "checks_completed": 23} if user_id else {"accuracy_rate": 0, "checks_completed": 0},
                    earned=False,
                    earned_at=None
                )
            ]
        
        achievements = await firestore_service.get_achievements(
            user_id=user_id,
            category=category,
            earned_only=earned_only
        )
        return achievements
        
    except Exception as e:
        logger.error(f"Error getting achievements: {e}")
        raise HTTPException(status_code=500, detail="Failed to get achievements")


@router.get("/badges", response_model=List[Badge])
async def get_user_badges(
    current_user: dict = Depends(get_current_user)
):
    """Get badges earned by the current user."""
    try:
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        if settings.use_mocks:
            return [
                Badge(
                    id="newcomer",
                    name="Newcomer",
                    description="Completed first fact check",
                    icon_url="/icons/newcomer-badge.png",
                    rarity="common",
                    earned_at="2025-09-04T09:00:00Z"
                ),
                Badge(
                    id="streak_champion",
                    name="Streak Champion",
                    description="Maintained 7-day activity streak",
                    icon_url="/icons/streak-badge.png", 
                    rarity="rare",
                    earned_at="2025-09-03T18:30:00Z"
                )
            ]
        
        badges = await firestore_service.get_user_badges(current_user["uid"])
        return badges
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user badges: {e}")
        raise HTTPException(status_code=500, detail="Failed to get user badges")


@router.get("/stats", response_model=UserStats)
async def get_user_stats(
    current_user: dict = Depends(get_current_user)
):
    """Get comprehensive user statistics."""
    try:
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        if settings.use_mocks:
            return UserStats(
                user_id=current_user["uid"],
                total_points=1250,
                level=5,
                level_progress=0.75,
                next_level_points=1500,
                checks_completed=87,
                accuracy_rate=88.5,
                current_streak=12,
                longest_streak=18,
                badges_earned=4,
                achievements_unlocked=8,
                content_shared=15,
                reports_submitted=3,
                learning_modules_completed=6,
                rank_global=42,
                rank_weekly=8
            )
        
        stats = await firestore_service.get_user_stats(current_user["uid"])
        return stats
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get user statistics")


@router.get("/challenges", response_model=List[Challenge])
async def get_active_challenges(
    current_user: dict = Depends(get_current_user)
):
    """Get active challenges for the user."""
    try:
        user_id = current_user.get("uid") if current_user else None
        
        if settings.use_mocks:
            return [
                Challenge(
                    id="weekly_checker",
                    title="Weekly Fact Checker",
                    description="Complete 20 fact checks this week",
                    type="weekly",
                    icon_url="/icons/weekly-challenge.png",
                    points_reward=100,
                    badge_reward="weekly_champion",
                    requirements={"checks_this_week": 20},
                    progress={"checks_this_week": 14} if user_id else {"checks_this_week": 0},
                    starts_at="2025-09-02T00:00:00Z",
                    ends_at="2025-09-09T00:00:00Z",
                    completed=False,
                    participants_count=234
                ),
                Challenge(
                    id="accuracy_challenge",
                    title="Precision Master",
                    description="Achieve 95%+ accuracy on next 10 checks",
                    type="skill",
                    icon_url="/icons/accuracy-challenge.png",
                    points_reward=150,
                    badge_reward="precision_master",
                    requirements={"accuracy_target": 95, "min_checks": 10},
                    progress={"current_accuracy": 92, "checks_completed": 7} if user_id else {"current_accuracy": 0, "checks_completed": 0},
                    starts_at="2025-09-01T00:00:00Z",
                    ends_at="2025-09-30T23:59:59Z",
                    completed=False,
                    participants_count=89
                )
            ]
        
        challenges = await firestore_service.get_active_challenges(user_id)
        return challenges
        
    except Exception as e:
        logger.error(f"Error getting challenges: {e}")
        raise HTTPException(status_code=500, detail="Failed to get challenges")


@router.post("/challenges/{challenge_id}/join")
async def join_challenge(
    challenge_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Join a challenge."""
    try:
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        if settings.use_mocks:
            return BaseResponse(
                success=True,
                message=f"Successfully joined challenge {challenge_id}"
            )
        
        result = await firestore_service.join_challenge(
            user_id=current_user["uid"],
            challenge_id=challenge_id
        )
        
        if not result:
            raise HTTPException(status_code=404, detail="Challenge not found or already joined")
        
        return BaseResponse(
            success=True,
            message="Successfully joined challenge"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error joining challenge: {e}")
        raise HTTPException(status_code=500, detail="Failed to join challenge")


@router.get("/points/history", response_model=List[PointsTransaction])
async def get_points_history(
    limit: int = 50,
    offset: int = 0,
    current_user: dict = Depends(get_current_user)
):
    """Get user's points transaction history."""
    try:
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        if settings.use_mocks:
            return [
                PointsTransaction(
                    id="tx_001",
                    user_id=current_user["uid"],
                    points=10,
                    reason="Fact check completed",
                    transaction_type="earned",
                    content_id="check_123",
                    created_at="2025-09-04T10:30:00Z"
                ),
                PointsTransaction(
                    id="tx_002", 
                    user_id=current_user["uid"],
                    points=50,
                    reason="Achievement unlocked: First Check",
                    transaction_type="bonus",
                    achievement_id="first_check",
                    created_at="2025-09-04T09:00:00Z"
                )
            ]
        
        transactions = await firestore_service.get_points_history(
            user_id=current_user["uid"],
            limit=limit,
            offset=offset
        )
        return transactions
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting points history: {e}")
        raise HTTPException(status_code=500, detail="Failed to get points history")


@router.get("/levels", response_model=List[LevelInfo])
async def get_level_info():
    """Get information about all available levels."""
    try:
        if settings.use_mocks:
            return [
                LevelInfo(
                    level=1,
                    title="Novice Checker",
                    points_required=0,
                    points_to_next=100,
                    perks=["Access to basic fact checking"],
                    icon_url="/icons/level-1.png"
                ),
                LevelInfo(
                    level=2,
                    title="Fact Explorer",
                    points_required=100,
                    points_to_next=200,
                    perks=["Unlock learning modules", "Join weekly challenges"],
                    icon_url="/icons/level-2.png"
                ),
                LevelInfo(
                    level=5,
                    title="Truth Guardian",
                    points_required=1000,
                    points_to_next=500,
                    perks=["Advanced analysis tools", "Priority support", "Custom badges"],
                    icon_url="/icons/level-5.png"
                )
            ]
        
        levels = await firestore_service.get_level_info()
        return levels
        
    except Exception as e:
        logger.error(f"Error getting level info: {e}")
        raise HTTPException(status_code=500, detail="Failed to get level information")


@router.post("/daily-reward/claim")
async def claim_daily_reward(
    current_user: dict = Depends(get_current_user)
):
    """Claim daily login reward."""
    try:
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        if settings.use_mocks:
            return {
                "success": True,
                "points_earned": 25,
                "streak_day": 3,
                "next_reward_in_hours": 24,
                "message": "Daily reward claimed! 3-day streak!"
            }
        
        result = await firestore_service.claim_daily_reward(current_user["uid"])
        
        if not result["success"]:
            raise HTTPException(
                status_code=400,
                detail=result.get("message", "Unable to claim daily reward")
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error claiming daily reward: {e}")
        raise HTTPException(status_code=500, detail="Failed to claim daily reward")
