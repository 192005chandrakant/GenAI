"""
Community endpoints for user interaction and content sharing.
"""
import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from app.models.dto import BaseResponse
from app.models.community_schemas import (
    CommunityPost, PostCreate, PostUpdate, Comment, CommentCreate,
    ShareRequest, ShareResponse, CommunityStats, UserReputation
)
from app.auth.firebase import get_current_user
from app.services.firestore_service import firestore_service
from app.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/posts", response_model=List[CommunityPost])
async def get_community_posts(
    limit: int = Query(20, le=100),
    offset: int = Query(0, ge=0),
    category: Optional[str] = None,
    sort_by: str = Query("recent", regex="^(recent|popular|trending)$"),
    current_user: Optional[dict] = Depends(get_current_user)
):
    """Get community posts with pagination and filtering."""
    try:
        if settings.use_mocks:
            return [
                CommunityPost(
                    id="post_001",
                    user_id="user_123",
                    author_name="TruthSeeker92",
                    author_avatar="https://via.placeholder.com/150",
                    author_reputation=1250,
                    title="Interesting fact-check about climate data",
                    content="Just analyzed this viral climate claim and found some interesting patterns...",
                    category="climate",
                    check_id="check_456",
                    check_score=75,
                    check_verdict="Mostly True",
                    likes_count=24,
                    comments_count=8,
                    shares_count=5,
                    created_at="2025-09-04T10:30:00Z",
                    updated_at="2025-09-04T10:30:00Z",
                    is_liked=True if current_user else False,
                    is_bookmarked=False if current_user else False,
                    tags=["climate", "science", "fact-check"],
                    visibility="public"
                ),
                CommunityPost(
                    id="post_002",
                    user_id="user_456",
                    author_name="FactChecker2000",
                    author_avatar="https://via.placeholder.com/150",
                    author_reputation=890,
                    title="Tips for identifying deepfake videos",
                    content="Here are some techniques I've learned for spotting AI-generated content...",
                    category="education",
                    check_id=None,
                    check_score=None,
                    check_verdict=None,
                    likes_count=56,
                    comments_count=12,
                    shares_count=15,
                    created_at="2025-09-03T15:45:00Z",
                    updated_at="2025-09-03T15:45:00Z",
                    is_liked=False if current_user else False,
                    is_bookmarked=True if current_user else False,
                    tags=["deepfake", "AI", "education"],
                    visibility="public"
                )
            ]
        
        posts = await firestore_service.get_community_posts(
            limit=limit,
            offset=offset,
            category=category,
            sort_by=sort_by,
            user_id=current_user.get("uid") if current_user else None
        )
        return posts
        
    except Exception as e:
        logger.error(f"Error getting community posts: {e}")
        raise HTTPException(status_code=500, detail="Failed to get community posts")


@router.post("/posts", response_model=CommunityPost)
async def create_community_post(
    post_data: PostCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new community post."""
    try:
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        if settings.use_mocks:
            return CommunityPost(
                id="post_new",
                user_id=current_user["uid"],
                author_name="Current User",
                author_avatar="https://via.placeholder.com/150",
                author_reputation=500,
                title=post_data.title,
                content=post_data.content,
                category=post_data.category,
                check_id=post_data.check_id,
                check_score=None,
                check_verdict=None,
                likes_count=0,
                comments_count=0,
                shares_count=0,
                created_at="2025-09-04T12:00:00Z",
                updated_at="2025-09-04T12:00:00Z",
                is_liked=False,
                is_bookmarked=False,
                tags=post_data.tags or [],
                visibility=post_data.visibility or "public"
            )
        
        post = await firestore_service.create_community_post(
            user_id=current_user["uid"],
            post_data=post_data
        )
        return post
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating community post: {e}")
        raise HTTPException(status_code=500, detail="Failed to create post")


@router.get("/posts/{post_id}", response_model=CommunityPost)
async def get_community_post(
    post_id: str,
    current_user: Optional[dict] = Depends(get_current_user)
):
    """Get a specific community post."""
    try:
        if settings.use_mocks:
            return CommunityPost(
                id=post_id,
                user_id="user_123",
                author_name="TruthSeeker92",
                author_avatar="https://via.placeholder.com/150",
                author_reputation=1250,
                title="Detailed analysis of viral claim",
                content="This is a comprehensive breakdown of why this claim is misleading...",
                category="analysis",
                check_id="check_789",
                check_score=85,
                check_verdict="Mostly False",
                likes_count=42,
                comments_count=18,
                shares_count=9,
                created_at="2025-09-04T09:00:00Z",
                updated_at="2025-09-04T09:00:00Z",
                is_liked=True if current_user else False,
                is_bookmarked=False if current_user else False,
                tags=["viral", "analysis", "misinformation"],
                visibility="public"
            )
        
        post = await firestore_service.get_community_post(
            post_id=post_id,
            user_id=current_user.get("uid") if current_user else None
        )
        
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        
        return post
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting community post: {e}")
        raise HTTPException(status_code=500, detail="Failed to get post")


@router.post("/posts/{post_id}/like")
async def like_post(
    post_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Like or unlike a community post."""
    try:
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        if settings.use_mocks:
            return BaseResponse(
                success=True,
                message="Post liked successfully"
            )
        
        result = await firestore_service.toggle_post_like(
            post_id=post_id,
            user_id=current_user["uid"]
        )
        
        return BaseResponse(
            success=True,
            message="Like toggled successfully",
            data={"is_liked": result["is_liked"], "likes_count": result["likes_count"]}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error liking post: {e}")
        raise HTTPException(status_code=500, detail="Failed to like post")


@router.post("/posts/{post_id}/share", response_model=ShareResponse)
async def share_post(
    post_id: str,
    share_data: ShareRequest,
    current_user: dict = Depends(get_current_user)
):
    """Share a community post."""
    try:
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        if settings.use_mocks:
            return ShareResponse(
                success=True,
                share_url=f"https://misinfoguard.com/community/posts/{post_id}",
                qr_code_url=f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=https://misinfoguard.com/community/posts/{post_id}",
                watermarked_image_url=None,
                message="Post shared successfully"
            )
        
        result = await firestore_service.share_post(
            post_id=post_id,
            user_id=current_user["uid"],
            platform=share_data.platform,
            message=share_data.message
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sharing post: {e}")
        raise HTTPException(status_code=500, detail="Failed to share post")


@router.get("/posts/{post_id}/comments", response_model=List[Comment])
async def get_post_comments(
    post_id: str,
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0),
    current_user: Optional[dict] = Depends(get_current_user)
):
    """Get comments for a specific post."""
    try:
        if settings.use_mocks:
            return [
                Comment(
                    id="comment_001",
                    post_id=post_id,
                    user_id="user_789",
                    author_name="CommentUser1",
                    author_avatar="https://via.placeholder.com/150",
                    author_reputation=750,
                    content="Great analysis! This really helped me understand the issue better.",
                    likes_count=5,
                    replies_count=2,
                    created_at="2025-09-04T11:15:00Z",
                    updated_at="2025-09-04T11:15:00Z",
                    is_liked=False if current_user else False,
                    parent_comment_id=None
                ),
                Comment(
                    id="comment_002",
                    post_id=post_id,
                    user_id="user_456",
                    author_name="AnotherUser",
                    author_avatar="https://via.placeholder.com/150",
                    author_reputation=320,
                    content="I have some additional sources that might be relevant here.",
                    likes_count=2,
                    replies_count=0,
                    created_at="2025-09-04T11:30:00Z",
                    updated_at="2025-09-04T11:30:00Z",
                    is_liked=True if current_user else False,
                    parent_comment_id=None
                )
            ]
        
        comments = await firestore_service.get_post_comments(
            post_id=post_id,
            limit=limit,
            offset=offset,
            user_id=current_user.get("uid") if current_user else None
        )
        return comments
        
    except Exception as e:
        logger.error(f"Error getting post comments: {e}")
        raise HTTPException(status_code=500, detail="Failed to get comments")


@router.post("/posts/{post_id}/comments", response_model=Comment)
async def create_comment(
    post_id: str,
    comment_data: CommentCreate,
    current_user: dict = Depends(get_current_user)
):
    """Add a comment to a post."""
    try:
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        if settings.use_mocks:
            return Comment(
                id="comment_new",
                post_id=post_id,
                user_id=current_user["uid"],
                author_name="Current User",
                author_avatar="https://via.placeholder.com/150",
                author_reputation=500,
                content=comment_data.content,
                likes_count=0,
                replies_count=0,
                created_at="2025-09-04T12:00:00Z",
                updated_at="2025-09-04T12:00:00Z",
                is_liked=False,
                parent_comment_id=comment_data.parent_comment_id
            )
        
        comment = await firestore_service.create_comment(
            post_id=post_id,
            user_id=current_user["uid"],
            comment_data=comment_data
        )
        return comment
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating comment: {e}")
        raise HTTPException(status_code=500, detail="Failed to create comment")


@router.get("/stats", response_model=CommunityStats)
async def get_community_stats():
    """Get overall community statistics."""
    try:
        if settings.use_mocks:
            return CommunityStats(
                total_posts=1247,
                total_users=89,
                total_comments=3456,
                total_likes=12789,
                total_shares=2341,
                active_users_today=23,
                trending_tags=["climate", "politics", "health", "technology", "education"]
            )
        
        stats = await firestore_service.get_community_stats()
        return stats
        
    except Exception as e:
        logger.error(f"Error getting community stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get community stats")


@router.get("/users/{user_id}/reputation", response_model=UserReputation)
async def get_user_reputation(user_id: str):
    """Get reputation information for a specific user."""
    try:
        if settings.use_mocks:
            return UserReputation(
                user_id=user_id,
                total_reputation=1250,
                posts_count=15,
                comments_count=47,
                likes_received=156,
                helpful_votes=89,
                accuracy_rating=92.5,
                trust_score=85,
                badges=["fact_master", "helpful_contributor"],
                level=5,
                rank_percentile=15
            )
        
        reputation = await firestore_service.get_user_reputation(user_id)
        return reputation
        
    except Exception as e:
        logger.error(f"Error getting user reputation: {e}")
        raise HTTPException(status_code=500, detail="Failed to get user reputation")


@router.post("/report")
async def report_content(
    content_id: str,
    content_type: str = Query(..., regex="^(post|comment)$"),
    reason: str = Query(..., min_length=10),
    current_user: dict = Depends(get_current_user)
):
    """Report inappropriate content."""
    try:
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        if settings.use_mocks:
            return BaseResponse(
                success=True,
                message="Content reported successfully. Our moderation team will review it."
            )
        
        result = await firestore_service.report_content(
            content_id=content_id,
            content_type=content_type,
            reason=reason,
            reporter_id=current_user["uid"]
        )
        
        return BaseResponse(
            success=True,
            message="Content reported successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error reporting content: {e}")
        raise HTTPException(status_code=500, detail="Failed to report content")
