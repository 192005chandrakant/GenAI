"""
Enhanced learning module endpoints with comprehensive educational content management,
media support, and community-driven learning features.
"""
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, Query, UploadFile, File, Form, status
from fastapi.responses import FileResponse

from app.models.enhanced_learning_schemas import (
    LearningModuleCreate, LearningModuleInDB, LearningModuleResponse,
    LearningModuleUpdate, ModuleSearchRequest, ModuleSearchResponse,
    UserProgress, CommunityContribution, LearningAnalytics,
    UserLearningDashboard, BulkModuleOperation, LearningStatistics,
    EducationalContent, MisinformationAwarenessModule, InteractiveExercise,
    MisinformationCategory, SkillLevel, ContentType, ModuleStatus
)
from app.models.enhanced_community_schemas import EnhancedMediaUpload
from app.auth.firebase import get_current_user, require_roles
from app.services.firestore_service import firestore_service
from app.services.cloudinary_service import cloudinary_service
from app.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()


# Learning Module Management Endpoints

@router.post("/modules", response_model=LearningModuleResponse, status_code=status.HTTP_201_CREATED)
async def create_learning_module(
    module_data: LearningModuleCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new learning module.
    
    Requires: Authenticated user (educators and above can create)
    """
    try:
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        user_id = current_user.get("uid")
        user_role = current_user.get("role", "learner")
        
        # Check permissions
        if user_role not in ["educator", "moderator", "admin"]:
            # Allow learners to create draft modules for review
            module_data.status = ModuleStatus.DRAFT
        
        # Create module in database
        module_id = await firestore_service.create_learning_module({
            **module_data.dict(),
            "created_by": user_id,
            "created_at": datetime.utcnow(),
            "status": module_data.status if hasattr(module_data, 'status') else ModuleStatus.DRAFT,
            "view_count": 0,
            "completion_count": 0,
            "version": 1
        })
        
        # Return created module
        module = await firestore_service.get_learning_module(module_id)
        if not module:
            raise HTTPException(status_code=500, detail="Failed to retrieve created module")
        
        # Convert to response format
        response = LearningModuleResponse(
            **module,
            creator_name=current_user.get("name", "Unknown"),
            is_featured=False
        )
        
        logger.info(f"Learning module created: {module_id} by user {user_id}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating learning module: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create learning module")


@router.get("/modules")
async def search_learning_modules(
    query: Optional[str] = Query(None, description="Search query"),
    category: Optional[str] = Query(None, description="Filter by category"),
    difficulty: Optional[str] = Query(None, description="Filter by skill level"),
    content_type: Optional[str] = Query(None, description="Filter by content type"),
    tags: Optional[List[str]] = Query(None, description="Filter by tags"),
    featured_only: bool = Query(False, description="Show only featured content"),
    sort_by: str = Query("created_at", description="Sort order"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Results per page"),
    current_user: Optional[dict] = Depends(get_current_user)
):
    """
    Search and filter learning modules.
    """
    try:
        # Build search criteria
        search_criteria = {
            "query": query,
            "category": category,
            "difficulty": difficulty,
            "content_type": content_type,
            "tags": tags,
            "featured_only": featured_only,
            "sort_by": sort_by,
            "page": page,
            "limit": limit,
            "status": "published"  # Only show published modules
        }
        
        user_id = current_user.get("uid") if current_user else None
        
        # Get modules from database
        modules, total_count = await firestore_service.search_learning_modules(
            search_criteria, user_id
        )
        
        # Calculate pagination
        total_pages = (total_count + limit - 1) // limit
        
        return {
            "modules": modules,
            "total_results": total_count,
            "page": page,
            "total_pages": total_pages,
            "filters_applied": {
                "category": category,
                "difficulty": difficulty,
                "content_type": content_type,
                "featured_only": featured_only
            }
        }
        
    except Exception as e:
        logger.error(f"Error searching learning modules: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to search learning modules")


from app.models.enhanced_learning_schemas import LearningModuleDetailResponse


@router.get("/modules/{module_id}", response_model=LearningModuleDetailResponse)
async def get_learning_module(
    module_id: str,
    current_user: Optional[dict] = Depends(get_current_user)
):
    """
    Get a specific learning module by ID.
    """
    try:
        # Prefer detailed module with structured content when available
        module = await firestore_service.get_learning_module_detail(module_id)
        if not module:
            raise HTTPException(status_code=404, detail="Learning module not found")
        
        # Check if user has access (published modules or own drafts)
        user_id = current_user.get("uid") if current_user else None
        if module.get("status") != "published":
            if not user_id or (module.get("created_by") != user_id and 
                             current_user.get("role", "learner") not in ["moderator", "admin"]):
                raise HTTPException(status_code=403, detail="Access denied")
        
        # Increment view count (if not the creator viewing)
        if user_id and user_id != module.get("created_by"):
            await firestore_service.increment_module_views(module_id)
        
        # Get user progress if authenticated
        user_progress = None
        if user_id:
            progress = await firestore_service.get_user_module_progress(user_id, module_id)
            if progress:
                user_progress = {
                    "completion_percentage": progress.get("completion_percentage", 0),
                    "current_section": progress.get("current_section", 0),
                    "bookmarked": progress.get("bookmarked", False),
                    "rating": progress.get("rating"),
                    "notes": progress.get("notes", "")
                }
        
        # Get creator information
        creator_name = "Unknown"
        if module.get("created_by"):
            creator_info = await firestore_service.get_user_profile(module["created_by"])
            if creator_info:
                creator_name = creator_info.get("name", "Unknown")
        
        response = LearningModuleDetailResponse(
            **module,
            creator_name=creator_name,
            user_progress=user_progress,
            is_featured=module.get("featured_until", datetime.utcnow()) > datetime.utcnow()
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting learning module {module_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get learning module")


@router.put("/modules/{module_id}", response_model=LearningModuleResponse)
async def update_learning_module(
    module_id: str,
    module_update: LearningModuleUpdate,
    current_user: dict = Depends(get_current_user)
):
    """
    Update a learning module.
    
    Requires: Module creator, moderator, or admin
    """
    try:
        user_id = current_user.get("uid")
        user_role = current_user.get("role", "learner")
        
        # Get existing module
        module = await firestore_service.get_learning_module(module_id)
        if not module:
            raise HTTPException(status_code=404, detail="Learning module not found")
        
        # Check permissions
        if (module.get("created_by") != user_id and 
            user_role not in ["moderator", "admin"]):
            raise HTTPException(status_code=403, detail="Permission denied")
        
        # Update module
        update_data = {k: v for k, v in module_update.dict().items() if v is not None}
        update_data["updated_at"] = datetime.utcnow()
        
        # Increment version if content changed
        if any(key in update_data for key in ["content_sections", "learning_objectives", "title"]):
            update_data["version"] = module.get("version", 1) + 1
        
        await firestore_service.update_learning_module(module_id, update_data)
        
        # Return updated module
        updated_module = await firestore_service.get_learning_module(module_id)
        response = LearningModuleResponse(
            **updated_module,
            creator_name=current_user.get("name", "Unknown"),
            is_featured=updated_module.get("featured_until", datetime.utcnow()) > datetime.utcnow()
        )
        
        logger.info(f"Learning module updated: {module_id} by user {user_id}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating learning module {module_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update learning module")


@router.delete("/modules/{module_id}")
async def delete_learning_module(
    module_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Delete a learning module.
    
    Requires: Module creator, moderator, or admin
    """
    try:
        user_id = current_user.get("uid")
        user_role = current_user.get("role", "learner")
        
        # Get existing module
        module = await firestore_service.get_learning_module(module_id)
        if not module:
            raise HTTPException(status_code=404, detail="Learning module not found")
        
        # Check permissions
        if (module.get("created_by") != user_id and 
            user_role not in ["moderator", "admin"]):
            raise HTTPException(status_code=403, detail="Permission denied")
        
        # Soft delete by updating status
        await firestore_service.update_learning_module(module_id, {
            "status": "archived",
            "archived_at": datetime.utcnow(),
            "archived_by": user_id
        })
        
        logger.info(f"Learning module deleted: {module_id} by user {user_id}")
        return {"success": True, "message": "Learning module deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting learning module {module_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete learning module")


# Media Upload Endpoints

@router.post("/modules/{module_id}/media", response_model=EnhancedMediaUpload)
async def upload_module_media(
    module_id: str,
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    alt_text: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),  # Comma-separated tags
    current_user: dict = Depends(get_current_user)
):
    """
    Upload media for a learning module.
    
    Requires: Module creator, moderator, or admin
    """
    try:
        user_id = current_user.get("uid")
        user_role = current_user.get("role", "learner")
        
        # Verify module exists and user has permission
        module = await firestore_service.get_learning_module(module_id)
        if not module:
            raise HTTPException(status_code=404, detail="Learning module not found")
        
        if (module.get("created_by") != user_id and 
            user_role not in ["moderator", "admin"]):
            raise HTTPException(status_code=403, detail="Permission denied")
        
        # Parse tags
        tag_list = [tag.strip() for tag in tags.split(",")] if tags else []
        
        # Upload to Cloudinary
        media_upload = await cloudinary_service.upload_educational_media(
            file=file,
            module_id=module_id,
            uploader_id=user_id,
            title=title,
            description=description,
            tags=tag_list
        )
        
        # Add alt_text if provided
        if alt_text:
            media_upload.alt_text = alt_text
        
        # Store media metadata in database
        await firestore_service.store_media_upload(media_upload.dict())
        
        logger.info(f"Media uploaded for module {module_id}: {media_upload.id}")
        return media_upload
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading media for module {module_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to upload media")


@router.get("/modules/{module_id}/media")
async def get_module_media(
    module_id: str,
    current_user: Optional[dict] = Depends(get_current_user)
):
    """
    Get all media uploads for a learning module.
    """
    try:
        # Verify module exists
        module = await firestore_service.get_learning_module(module_id)
        if not module:
            raise HTTPException(status_code=404, detail="Learning module not found")
        
        # Get media uploads
        media_uploads = await firestore_service.get_module_media(module_id)
        
        return {"media_uploads": media_uploads}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting media for module {module_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get module media")


# User Progress Endpoints

@router.post("/modules/{module_id}/progress")
async def update_user_progress(
    module_id: str,
    progress_data: Dict[str, Any],
    current_user: dict = Depends(get_current_user)
):
    """
    Update user's progress in a learning module.
    """
    try:
        user_id = current_user.get("uid")
        
        # Verify module exists
        module = await firestore_service.get_learning_module(module_id)
        if not module:
            raise HTTPException(status_code=404, detail="Learning module not found")
        
        # Update progress
        await firestore_service.update_user_progress(user_id, module_id, progress_data)
        
        # Check if module is completed
        if progress_data.get("completion_percentage", 0) >= 100:
            await firestore_service.increment_module_completions(module_id)
            
            # Award points/achievements
            await firestore_service.award_completion_points(user_id, module_id)
        
        return {"success": True, "message": "Progress updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating progress for module {module_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update progress")


@router.get("/modules/{module_id}/progress", response_model=UserProgress)
async def get_user_progress(
    module_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get user's progress in a learning module.
    """
    try:
        user_id = current_user.get("uid")
        
        progress = await firestore_service.get_user_module_progress(user_id, module_id)
        if not progress:
            raise HTTPException(status_code=404, detail="Progress not found")
        
        return UserProgress(**progress)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting progress for module {module_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get progress")


# User Dashboard Endpoints

@router.get("/dashboard", response_model=UserLearningDashboard)
async def get_user_dashboard(
    current_user: dict = Depends(get_current_user)
):
    """
    Get user's learning dashboard with personalized recommendations.
    """
    try:
        user_id = current_user.get("uid")
        
        # Get user's learning statistics
        dashboard_data = await firestore_service.get_user_learning_dashboard(user_id)
        
        return UserLearningDashboard(**dashboard_data)
        
    except Exception as e:
        logger.error(f"Error getting user dashboard: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get dashboard")


# Community Contribution Endpoints

@router.post("/contributions", response_model=CommunityContribution)
async def submit_community_contribution(
    contribution: CommunityContribution,
    current_user: dict = Depends(get_current_user)
):
    """
    Submit a community contribution (new module or improvement suggestion).
    """
    try:
        user_id = current_user.get("uid")
        contribution.contributor_id = user_id
        contribution.created_at = datetime.utcnow()
        
        # Store contribution
        contribution_id = await firestore_service.create_community_contribution(contribution.dict())
        contribution.id = contribution_id
        
        logger.info(f"Community contribution submitted: {contribution_id} by user {user_id}")
        return contribution
        
    except Exception as e:
        logger.error(f"Error submitting community contribution: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to submit contribution")


# Admin Endpoints

@router.get("/admin/statistics", response_model=LearningStatistics)
async def get_learning_statistics(
    current_user: dict = Depends(require_roles(["admin", "moderator"]))
):
    """
    Get comprehensive learning platform statistics.
    
    Requires: Admin or moderator role
    """
    try:
        stats = await firestore_service.get_learning_statistics()
        return LearningStatistics(**stats)
        
    except Exception as e:
        logger.error(f"Error getting learning statistics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get statistics")


@router.post("/admin/modules/bulk-operation")
async def bulk_module_operation(
    operation: BulkModuleOperation,
    current_user: dict = Depends(require_roles(["admin", "moderator"]))
):
    """
    Perform bulk operations on learning modules.
    
    Requires: Admin or moderator role
    """
    try:
        user_id = current_user.get("uid")
        
        # Perform bulk operation
        result = await firestore_service.bulk_module_operation(
            operation.module_ids,
            operation.operation,
            operation.parameters,
            user_id,
            operation.reason
        )
        
        logger.info(f"Bulk operation {operation.operation} performed on {len(operation.module_ids)} modules by {user_id}")
        return result
        
    except Exception as e:
        logger.error(f"Error performing bulk operation: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to perform bulk operation")


@router.get("/categories")
async def get_misinformation_categories():
    """
    Get available misinformation categories for learning modules.
    """
    categories = [
        {
            "value": category.value,
            "label": category.value.replace("_", " ").title(),
            "description": f"Content related to {category.value.replace('_', ' ')}"
        }
        for category in MisinformationCategory
    ]
    
    return {"categories": categories}


@router.get("/skill-levels")
async def get_skill_levels():
    """
    Get available skill levels for learning modules.
    """
    levels = [
        {
            "value": level.value,
            "label": level.value.title(),
            "description": f"{level.value.title()} level content"
        }
        for level in SkillLevel
    ]
    
    return {"skill_levels": levels}


@router.get("/content-types")
async def get_content_types():
    """
    Get available content types for learning modules.
    """
    types = [
        {
            "value": content_type.value,
            "label": content_type.value.replace("_", " ").title(),
            "description": f"{content_type.value.replace('_', ' ').title()} content"
        }
        for content_type in ContentType
    ]
    
    return {"content_types": types}


# Featured Content Endpoints

@router.get("/featured", response_model=List[LearningModuleResponse])
async def get_featured_modules(
    limit: int = Query(10, ge=1, le=50),
    current_user: Optional[dict] = Depends(get_current_user)
):
    """
    Get featured learning modules.
    """
    try:
        user_id = current_user.get("uid") if current_user else None
        
        modules = await firestore_service.get_featured_modules(limit, user_id)
        
        # Convert to response format
        responses = []
        for module in modules:
            user_progress = None
            if user_id:
                progress = await firestore_service.get_user_module_progress(user_id, module["id"])
                if progress:
                    user_progress = {
                        "completion_percentage": progress.get("completion_percentage", 0),
                        "bookmarked": progress.get("bookmarked", False)
                    }
            
            response = LearningModuleResponse(
                **module,
                user_progress=user_progress,
                is_featured=True
            )
            responses.append(response)
        
        return responses
        
    except Exception as e:
        logger.error(f"Error getting featured modules: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get featured modules")