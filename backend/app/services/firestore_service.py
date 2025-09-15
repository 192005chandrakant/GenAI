"""
Firestore service for database operations.
"""
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
from google.cloud import firestore
from google.cloud.firestore_v1.base_query import FieldFilter

from app.core.config import settings
from app.models.schemas import (
    UserCreate,
    UserResponse,
    UserUpdate,
    ReportCreate,
    ReportResponse,
    ReportStatus,
    PointsTransaction,
    LeaderboardEntry,
    LearningModule,
    QuizSubmission,
    ContentAnalysisResponse,
)

logger = logging.getLogger(__name__)


class FirestoreService:
    """Service for Firestore database operations."""
    
    def __init__(self):
        """Initialize Firestore client."""
        self.use_mock = False
        # Initialize collections as None first
        self.users_collection = None
        self.reports_collection = None
        self.content_collection = None
        self.points_collection = None
        self.learning_collection = None
        self.quiz_collection = None
        
        try:
            if settings.use_mocks or settings.google_cloud_project == "local-gcp-project":
                logger.info("Using mock Firestore service")
                self.use_mock = True
                self.db = None
                # For mock mode, we still initialize collection references to prevent errors
                self._init_mock_collections()
            else:
                self.db = firestore.Client(project=settings.google_cloud_project)
                self.users_collection = self.db.collection("users")
                self.reports_collection = self.db.collection("reports")
                self.content_collection = self.db.collection("content_analysis")
                self.points_collection = self.db.collection("points_transactions")
                self.learning_collection = self.db.collection("learning_modules")
                self.quiz_collection = self.db.collection("quiz_submissions")
                logger.info("Firestore client initialized successfully")
        except Exception as e:
            logger.warning(f"Failed to initialize Firestore client: {str(e)}")
            logger.info("Falling back to mock Firestore service")
            self.use_mock = True
            self.db = None
            self._init_mock_collections()
    
    def _init_mock_collections(self):
        """Initialize mock collection references to prevent attribute errors."""
        # Create mock collection objects that won't actually be used
        # but prevent AttributeError when accessed
        class MockCollection:
            def add(self, data):
                return None, type('MockDocRef', (), {'id': 'mock_doc_id'})()
            def document(self, doc_id):
                return type('MockDoc', (), {'get': lambda: type('MockDocData', (), {'exists': False})()})()
            def where(self, **kwargs):
                return self
            def order_by(self, field, direction=None):
                return self
            def limit(self, num):
                return self
            def stream(self):
                return []
            def update(self, data):
                pass
            def delete(self):
                pass
        
        self.users_collection = MockCollection()
        self.reports_collection = MockCollection()
        self.content_collection = MockCollection()
        self.points_collection = MockCollection()
        self.learning_collection = MockCollection()
        self.quiz_collection = MockCollection()
    
    # User Operations
    async def create_user(self, user_data: UserCreate) -> UserResponse:
        """Create a new user."""
        if self.use_mock:
            logger.info(f"Mock: Creating user {user_data.email}")
            return UserResponse(
                uid=user_data.uid,
                email=user_data.email,
                name=user_data.name or "Mock User",
                display_name=user_data.display_name,
                profile_image=user_data.profile_image,
                role=user_data.role,
                created_at=datetime.now(),
                points=0,
                level=1
            )
        
        try:
            user_doc = {
                "email": user_data.email,
                "name": user_data.name,
                "avatar_url": user_data.avatar_url,
                "points": 0,
                "level": 1,
                "total_reports": 0,
                "correct_detections": 0,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            doc_ref = self.users_collection.add(user_doc)[1]
            user_doc["id"] = doc_ref.id
            
            return UserResponse(**user_doc)
            
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            raise
    
    async def get_user_by_id(self, user_id: str) -> Optional[UserResponse]:
        """Get user by ID."""
        try:
            doc = self.users_collection.document(user_id).get()
            if doc.exists:
                user_data = doc.to_dict()
                user_data["id"] = doc.id
                return UserResponse(**user_data)
            return None
        except Exception as e:
            logger.error(f"Error getting user by ID: {str(e)}")
            return None
    
    async def get_user_by_email(self, email: str) -> Optional[UserResponse]:
        """Get user by email."""
        try:
            query = self.users_collection.where(filter=FieldFilter("email", "==", email))
            docs = query.stream()
            
            for doc in docs:
                user_data = doc.to_dict()
                user_data["id"] = doc.id
                return UserResponse(**user_data)
            
            return None
        except Exception as e:
            logger.error(f"Error getting user by email: {str(e)}")
            return None
    
    async def update_user(self, user_id: str, user_data: UserUpdate) -> Optional[UserResponse]:
        """Update user information."""
        try:
            update_data = user_data.dict(exclude_unset=True)
            update_data["updated_at"] = datetime.utcnow()
            
            doc_ref = self.users_collection.document(user_id)
            doc_ref.update(update_data)
            
            return await self.get_user_by_id(user_id)
        except Exception as e:
            logger.error(f"Error updating user: {str(e)}")
            return None
    
    async def delete_user(self, user_id: str) -> bool:
        """Delete a user."""
        try:
            self.users_collection.document(user_id).delete()
            return True
        except Exception as e:
            logger.error(f"Error deleting user: {str(e)}")
            return False
    
    # Content Analysis Operations
    async def save_content_analysis(self, analysis: ContentAnalysisResponse) -> str:
        """Save content analysis result."""
        try:
            analysis_data = analysis.dict()
            doc_ref = self.content_collection.add(analysis_data)[1]
            return doc_ref.id
        except Exception as e:
            logger.error(f"Error saving content analysis: {str(e)}")
            raise
    
    async def get_content_analysis(self, content_id: str) -> Optional[ContentAnalysisResponse]:
        """Get content analysis by ID."""
        try:
            query = self.content_collection.where(filter=FieldFilter("content_id", "==", content_id))
            docs = query.stream()
            
            for doc in docs:
                return ContentAnalysisResponse(**doc.to_dict())
            
            return None
        except Exception as e:
            logger.error(f"Error getting content analysis: {str(e)}")
            return None
    
    # Report Operations
    async def create_report(self, report_data: ReportCreate) -> ReportResponse:
        """Create a new report."""
        try:
            report_doc = {
                "content_id": report_data.content_id,
                "user_id": report_data.user_id,
                "status": ReportStatus.PENDING,
                "additional_notes": report_data.additional_notes,
                "category": report_data.category,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            doc_ref = self.reports_collection.add(report_doc)[1]
            report_doc["id"] = doc_ref.id
            
            return ReportResponse(**report_doc)
        except Exception as e:
            logger.error(f"Error creating report: {str(e)}")
            raise
    
    async def get_report(self, report_id: str) -> Optional[ReportResponse]:
        """Get report by ID."""
        try:
            doc = self.reports_collection.document(report_id).get()
            if doc.exists:
                report_data = doc.to_dict()
                report_data["id"] = doc.id
                return ReportResponse(**report_data)
            return None
        except Exception as e:
            logger.error(f"Error getting report: {str(e)}")
            return None
    
    async def update_report(self, report_id: str, status: ReportStatus, admin_notes: Optional[str] = None, reviewed_by: Optional[str] = None) -> Optional[ReportResponse]:
        """Update report status."""
        try:
            update_data = {
                "status": status,
                "updated_at": datetime.utcnow()
            }
            
            if admin_notes is not None:
                update_data["admin_notes"] = admin_notes
            
            if reviewed_by is not None:
                update_data["reviewed_by"] = reviewed_by
            
            doc_ref = self.reports_collection.document(report_id)
            doc_ref.update(update_data)
            
            return await self.get_report(report_id)
        except Exception as e:
            logger.error(f"Error updating report: {str(e)}")
            return None
    
    async def get_reports_by_user(self, user_id: str, limit: int = 50) -> List[ReportResponse]:
        """Get reports by user ID."""
        try:
            query = self.reports_collection.where(filter=FieldFilter("user_id", "==", user_id)).order_by("created_at", direction=firestore.Query.DESCENDING).limit(limit)
            docs = query.stream()
            
            reports = []
            for doc in docs:
                report_data = doc.to_dict()
                report_data["id"] = doc.id
                reports.append(ReportResponse(**report_data))
            
            return reports
        except Exception as e:
            logger.error(f"Error getting reports by user: {str(e)}")
            return []
    
    async def get_pending_reports(self, limit: int = 50) -> List[ReportResponse]:
        """Get pending reports for admin review."""
        try:
            query = self.reports_collection.where(filter=FieldFilter("status", "==", ReportStatus.PENDING)).order_by("created_at", direction=firestore.Query.DESCENDING).limit(limit)
            docs = query.stream()
            
            reports = []
            for doc in docs:
                report_data = doc.to_dict()
                report_data["id"] = doc.id
                reports.append(ReportResponse(**report_data))
            
            return reports
        except Exception as e:
            logger.error(f"Error getting pending reports: {str(e)}")
            return []
    
    # Points and Gamification Operations
    async def add_points(self, user_id: str, points: int, reason: str, content_id: Optional[str] = None) -> bool:
        """Add points to user and record transaction."""
        try:
            # Record transaction
            transaction_doc = {
                "user_id": user_id,
                "points": points,
                "reason": reason,
                "content_id": content_id,
                "created_at": datetime.utcnow()
            }
            
            self.points_collection.add(transaction_doc)
            
            # Update user points
            user_ref = self.users_collection.document(user_id)
            user_doc = user_ref.get()
            
            if user_doc.exists:
                current_points = user_doc.to_dict().get("points", 0)
                new_points = current_points + points
                
                # Calculate new level (every 100 points = 1 level)
                new_level = (new_points // 100) + 1
                
                user_ref.update({
                    "points": new_points,
                    "level": new_level,
                    "updated_at": datetime.utcnow()
                })
                
                return True
            
            return False
        except Exception as e:
            logger.error(f"Error adding points: {str(e)}")
            return False
    
    async def get_user_points_history(self, user_id: str, limit: int = 50) -> List[PointsTransaction]:
        """Get user's points transaction history."""
        try:
            query = self.points_collection.where(filter=FieldFilter("user_id", "==", user_id)).order_by("created_at", direction=firestore.Query.DESCENDING).limit(limit)
            docs = query.stream()
            
            transactions = []
            for doc in docs:
                transaction_data = doc.to_dict()
                transactions.append(PointsTransaction(**transaction_data))
            
            return transactions
        except Exception as e:
            logger.error(f"Error getting points history: {str(e)}")
            return []
    
    async def get_leaderboard(self, limit: int = 100) -> List[LeaderboardEntry]:
        """Get leaderboard of top users."""
        try:
            query = self.users_collection.order_by("points", direction=firestore.Query.DESCENDING).limit(limit)
            docs = query.stream()
            
            leaderboard = []
            rank = 1
            
            for doc in docs:
                user_data = doc.to_dict()
                entry = LeaderboardEntry(
                    user_id=doc.id,
                    user_name=user_data.get("name", "Unknown"),
                    points=user_data.get("points", 0),
                    level=user_data.get("level", 1),
                    rank=rank
                )
                leaderboard.append(entry)
                rank += 1
            
            return leaderboard
        except Exception as e:
            logger.error(f"Error getting leaderboard: {str(e)}")
            return []
    
    # Learning Module Operations
    async def create_learning_module(self, module_data: dict) -> str:
        """Create a new learning module."""
        try:
            module_doc = {
                **module_data,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            doc_ref = self.learning_collection.add(module_doc)[1]
            return doc_ref.id
        except Exception as e:
            logger.error(f"Error creating learning module: {str(e)}")
            raise
    
    async def get_learning_modules(self, limit: int = 50) -> List[LearningModule]:
        """Get all learning modules."""
        try:
            query = self.learning_collection.order_by("created_at", direction=firestore.Query.DESCENDING).limit(limit)
            docs = query.stream()
            
            modules = []
            for doc in docs:
                module_data = doc.to_dict()
                module_data["id"] = doc.id
                modules.append(LearningModule(**module_data))
            
            return modules
        except Exception as e:
            logger.error(f"Error getting learning modules: {str(e)}")
            return []
    
    async def get_learning_module(self, module_id: str) -> Optional[LearningModule]:
        """Get learning module by ID."""
        try:
            doc = self.learning_collection.document(module_id).get()
            if doc.exists:
                module_data = doc.to_dict()
                module_data["id"] = doc.id
                return LearningModule(**module_data)
            return None
        except Exception as e:
            logger.error(f"Error getting learning module: {str(e)}")
            return None

    async def get_learning_module_detail(self, module_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed learning module including structured sections and exercises.

        In mock mode, return a rich structured module for interactive UI development.
        """
        if self.use_mock:
            # Provide detailed, structured mock module content
            return {
                "id": module_id,
                "title": "Spotting Deepfakes in the Wild",
                "description": "Hands-on module to learn how to identify AI-generated images and videos.",
                "content_type": "interactive",
                "skill_level": "intermediate",
                "misinformation_category": "deepfakes_manipulation",
                "estimated_duration_minutes": 40,
                "learning_objectives": [
                    "Recognize common deepfake artifacts",
                    "Use forensic tools for detection",
                    "Understand ethical considerations"
                ],
                "status": "published",
                "created_by": "system",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "view_count": 0,
                "completion_count": 0,
                "average_rating": 4.6,
                "total_ratings": 18,
                "tags": ["deepfakes", "media-literacy"],
                "prerequisites": [],
                "preview_content": "Learn to spot AI-generated media with practical tips and tools.",
                "thumbnail_url": None,
                # Legacy content body (optional)
                "content": "# Spotting Deepfakes\n\nThis module walks you through practical techniques...",
                # Structured content sections
                "content_sections": [
                    {
                        "title": "What Are Deepfakes?",
                        "description": "Overview and context",
                        "content_body": "Deepfakes are synthetic media where a person in an existing image or video is replaced with someone else's likeness...",
                        "content_type": "text",
                        "skill_level": "beginner",
                        "estimated_duration_minutes": 5,
                        "tags": ["overview"],
                        "keywords": ["deepfake", "synthetic media"],
                        "learning_objectives": ["Define deepfakes", "Understand use cases"],
                        "prerequisites": [],
                        "media_attachments": [],
                        "external_resources": []
                    },
                    {
                        "title": "Visual Artifacts",
                        "description": "Common signs in images and videos",
                        "content_body": "Look for irregular eye blinking, mismatched lighting, warping around the face edges...",
                        "content_type": "image",
                        "skill_level": "intermediate",
                        "estimated_duration_minutes": 8,
                        "tags": ["artifacts"],
                        "keywords": ["visual", "forensics"],
                        "learning_objectives": ["Identify visual artifacts"],
                        "prerequisites": [],
                        "media_attachments": ["upload_example_artifact_1"],
                        "external_resources": []
                    }
                ],
                # Interactive exercises (e.g., quiz)
                "interactive_exercises": [
                    {
                        "id": "quiz_1",
                        "exercise_type": "quiz",
                        "title": "Deepfake Basics Quiz",
                        "instructions": "Answer the following questions to check your understanding.",
                        "content": {
                            "questions": [
                                {
                                    "id": "q1",
                                    "type": "single",
                                    "prompt": "Which of the following is a common visual sign of a deepfake?",
                                    "options": [
                                        "Consistent eye blinking",
                                        "Mismatched lighting on the face",
                                        "Perfect lip-sync",
                                        "Natural shadows"
                                    ],
                                    "answer": 1
                                },
                                {
                                    "id": "q2",
                                    "type": "true_false",
                                    "prompt": "All deepfakes can be detected with the naked eye.",
                                    "answer": False
                                }
                            ]
                        },
                        "correct_answers": None,
                        "hints": ["Look at lighting and reflections"],
                        "explanation": "Visual inconsistencies are common in lower-quality deepfakes.",
                        "points_possible": 10
                    }
                ],
                "media_uploads": [],
                "metadata": {"fact_check_score": 92, "media_urls": []}
            }

        try:
            # Real implementation: fetch module document with nested fields
            doc = self.learning_collection.document(module_id).get()
            if doc.exists:
                module_data = doc.to_dict()
                module_data["id"] = doc.id
                return module_data
            return None
        except Exception as e:
            logger.error(f"Error getting detailed learning module: {str(e)}")
            return None
    
    # Quiz Operations
    async def save_quiz_submission(self, submission: QuizSubmission) -> str:
        """Save quiz submission."""
        try:
            submission_data = submission.dict()
            submission_data["created_at"] = datetime.utcnow()
            
            doc_ref = self.quiz_collection.add(submission_data)[1]
            return doc_ref.id
        except Exception as e:
            logger.error(f"Error saving quiz submission: {str(e)}")
            raise
    
    async def get_user_quiz_submissions(self, user_id: str, limit: int = 50) -> List[QuizSubmission]:
        """Get user's quiz submissions."""
        try:
            query = self.quiz_collection.where(filter=FieldFilter("user_id", "==", user_id)).order_by("created_at", direction=firestore.Query.DESCENDING).limit(limit)
            docs = query.stream()
            
            submissions = []
            for doc in docs:
                submission_data = doc.to_dict()
                submissions.append(QuizSubmission(**submission_data))
            
            return submissions
        except Exception as e:
            logger.error(f"Error getting quiz submissions: {str(e)}")
            return []
    
    # Analytics Operations
    async def get_analytics_summary(self) -> Dict[str, Any]:
        """Get analytics summary for admin dashboard."""
        if self.use_mock:
            logger.info("Mock: Returning sample analytics data")
            return {
                "total_users": 125,
                "total_reports": 89,
                "average_points": 156.7,
                "top_reporters": [
                    {"user_id": "mock_user_1", "name": "Mock User 1", "total_reports": 15},
                    {"user_id": "mock_user_2", "name": "Mock User 2", "total_reports": 12},
                    {"user_id": "mock_user_3", "name": "Mock User 3", "total_reports": 10}
                ]
            }
        
        try:
            # Get total users
            users_docs = self.users_collection.stream()
            total_users = sum(1 for _ in users_docs)
            
            # Get total reports
            reports_docs = self.reports_collection.stream()
            total_reports = sum(1 for _ in reports_docs)
            
            # Get average points
            users_docs = self.users_collection.stream()
            total_points = sum(doc.to_dict().get("points", 0) for doc in users_docs)
            avg_points = total_points / total_users if total_users > 0 else 0
            
            # Get top reporters
            top_reporters_query = self.users_collection.order_by("total_reports", direction=firestore.Query.DESCENDING).limit(10)
            top_reporters = []
            for doc in top_reporters_query.stream():
                user_data = doc.to_dict()
                top_reporters.append({
                    "user_id": doc.id,
                    "name": user_data.get("name", "Unknown"),
                    "total_reports": user_data.get("total_reports", 0)
                })
            
            return {
                "total_users": total_users,
                "total_reports": total_reports,
                "average_points": avg_points,
                "top_reporters": top_reporters
            }
        except Exception as e:
            logger.error(f"Error getting analytics summary: {str(e)}")
            return {
                "total_users": 0,
                "total_reports": 0,
                "average_points": 0,
                "top_reporters": []
            }

    # Enhanced Community Methods
    async def search_community_posts(self, search_criteria: Dict[str, Any], user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search community posts with filters."""
        if self.use_mock:
            logger.info("Mock: Returning sample community posts")
            return [
                {
                    "id": "post_1",
                    "title": "Understanding Deepfakes",
                    "content": "Learn how to identify deepfake videos and images...",
                    "author_id": "user_1",
                    "author_name": "Alex Johnson",
                    "category": "misinformation-awareness",
                    "post_type": "educational",
                    "created_at": datetime.utcnow().isoformat(),
                    "likes_count": 15,
                    "comments_count": 8,
                    "is_liked": False,
                    "is_bookmarked": False
                },
                {
                    "id": "post_2", 
                    "title": "Fact-Checking Social Media Posts",
                    "content": "Best practices for verifying information on social media...",
                    "author_id": "user_2",
                    "author_name": "Sarah Chen",
                    "category": "fact-checking",
                    "post_type": "discussion",
                    "created_at": datetime.utcnow().isoformat(),
                    "likes_count": 23,
                    "comments_count": 12,
                    "is_liked": False,
                    "is_bookmarked": False
                }
            ]
        
        try:
            # In real implementation, this would query Firestore
            # For now, return empty list
            return []
        except Exception as e:
            logger.error(f"Error searching community posts: {str(e)}")
            return []

    async def create_enhanced_community_post(self, post_data: Dict[str, Any]) -> str:
        """Create a new community post."""
        if self.use_mock:
            import uuid
            post_id = str(uuid.uuid4())
            logger.info(f"Mock: Created community post {post_id}")
            return post_id
        
        try:
            # In real implementation, this would create in Firestore
            return "mock_post_id"
        except Exception as e:
            logger.error(f"Error creating community post: {str(e)}")
            raise

    async def get_enhanced_community_post(self, post_id: str) -> Optional[Dict[str, Any]]:
        """Get a community post by ID."""
        if self.use_mock:
            logger.info(f"Mock: Getting community post {post_id}")
            return {
                "id": post_id,
                "title": "Sample Post",
                "content": "This is a sample post content...",
                "author_id": "user_1",
                "author_name": "Mock User",
                "category": "misinformation-awareness",
                "post_type": "discussion",
                "created_at": datetime.utcnow().isoformat(),
                "likes_count": 5,
                "comments_count": 3,
                "allow_comments": True
            }
        
        try:
            # In real implementation, this would query Firestore
            return None
        except Exception as e:
            logger.error(f"Error getting community post: {str(e)}")
            return None

    async def update_enhanced_community_post(self, post_id: str, update_data: Dict[str, Any]) -> None:
        """Update a community post."""
        if self.use_mock:
            logger.info(f"Mock: Updated community post {post_id}")
            return
        
        try:
            # In real implementation, this would update in Firestore
            pass
        except Exception as e:
            logger.error(f"Error updating community post: {str(e)}")
            raise

    async def store_media_upload(self, media_data: Dict[str, Any]) -> None:
        """Store media upload metadata."""
        if self.use_mock:
            logger.info("Mock: Stored media upload metadata")
            return
        
        try:
            # In real implementation, this would store in Firestore
            pass
        except Exception as e:
            logger.error(f"Error storing media upload: {str(e)}")
            raise

    async def get_user_post_interactions(self, user_id: str, post_id: str) -> List[Dict[str, Any]]:
        """Get user interactions for a post."""
        if self.use_mock:
            return []
        
        try:
            # In real implementation, this would query Firestore
            return []
        except Exception as e:
            logger.error(f"Error getting user interactions: {str(e)}")
            return []

    async def increment_post_views(self, post_id: str) -> None:
        """Increment post view count."""
        if self.use_mock:
            return
        
        try:
            # In real implementation, this would update Firestore
            pass
        except Exception as e:
            logger.error(f"Error incrementing post views: {str(e)}")

    # Enhanced Learning Methods
    async def search_learning_modules(self, search_criteria: Dict[str, Any], user_id: Optional[str] = None) -> tuple[List[Dict[str, Any]], int]:
        """Search learning modules with filters."""
        if self.use_mock:
            logger.info("Mock: Returning sample learning modules")
            modules = [
                {
                    "id": "module_1",
                    "title": "Introduction to Misinformation",
                    "description": "Learn the basics of identifying misinformation and fake news.",
                    "content": "# Introduction to Misinformation\n\nThis module covers the fundamentals of misinformation detection...",
                    "category": "misinformation-awareness",
                    "difficulty_level": "beginner",
                    "estimated_duration_minutes": 30,
                    "tags": ["misinformation", "basics", "detection"],
                    "author_id": "system",
                    "author_name": "MisinfoGuard Team",
                    "is_published": True,
                    "created_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat(),
                    "completion_count": 125,
                    "average_rating": 4.5,
                    "rating_count": 20,
                    "content_type": "text",
                    "interactive_elements": [],
                    "prerequisites": [],
                    "learning_objectives": ["Understand basic misinformation concepts", "Learn detection techniques"]
                },
                {
                    "id": "module_2",
                    "title": "Spotting Deepfakes",
                    "description": "Advanced techniques for identifying AI-generated media.",
                    "content": "# Spotting Deepfakes\n\nDeepfakes are becoming increasingly sophisticated...",
                    "category": "media-literacy",
                    "difficulty_level": "intermediate", 
                    "estimated_duration_minutes": 45,
                    "tags": ["deepfakes", "AI", "video", "image"],
                    "author_id": "system",
                    "author_name": "MisinfoGuard Team",
                    "is_published": True,
                    "created_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat(),
                    "completion_count": 89,
                    "average_rating": 4.7,
                    "rating_count": 15,
                    "content_type": "text",
                    "interactive_elements": [],
                    "prerequisites": ["module_1"],
                    "learning_objectives": ["Identify deepfake videos", "Understand AI generation techniques"]
                },
                {
                    "id": "module_3",
                    "title": "Social Media Fact-Checking",
                    "description": "Tools and techniques for verifying social media content.",
                    "content": "# Social Media Fact-Checking\n\nSocial media is a breeding ground for misinformation...",
                    "category": "fact-checking",
                    "difficulty_level": "beginner",
                    "estimated_duration_minutes": 25,
                    "tags": ["social-media", "verification", "tools"],
                    "author_id": "system", 
                    "author_name": "MisinfoGuard Team",
                    "is_published": True,
                    "created_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat(),
                    "completion_count": 156,
                    "average_rating": 4.3,
                    "rating_count": 25,
                    "content_type": "text",
                    "interactive_elements": [],
                    "prerequisites": [],
                    "learning_objectives": ["Use fact-checking tools", "Verify social media posts"]
                },
                {
                    "id": "module_4",
                    "title": "Understanding Bias in News",
                    "description": "How to identify and account for bias in news reporting.",
                    "content": "# Understanding Bias in News\n\nMedia bias can influence how information is presented...",
                    "category": "news-analysis",
                    "difficulty_level": "intermediate",
                    "estimated_duration_minutes": 40,
                    "tags": ["bias", "news", "analysis", "critical-thinking"],
                    "author_id": "system",
                    "author_name": "MisinfoGuard Team",
                    "is_published": True,
                    "created_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat(),
                    "completion_count": 67,
                    "average_rating": 4.4,
                    "rating_count": 12,
                    "content_type": "text",
                    "interactive_elements": [],
                    "prerequisites": [],
                    "learning_objectives": ["Identify media bias", "Analyze news sources"]
                },
                {
                    "id": "module_5",
                    "title": "Digital Citizenship Basics",
                    "description": "Responsible behavior and critical thinking in digital spaces.",
                    "content": "# Digital Citizenship Basics\n\nBeing a good digital citizen means...",
                    "category": "digital-citizenship",
                    "difficulty_level": "beginner",
                    "estimated_duration_minutes": 35,
                    "tags": ["digital-citizenship", "responsibility", "ethics"],
                    "author_id": "system",
                    "author_name": "MisinfoGuard Team", 
                    "is_published": True,
                    "created_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat(),
                    "completion_count": 98,
                    "average_rating": 4.6,
                    "rating_count": 18,
                    "content_type": "text",
                    "interactive_elements": [],
                    "prerequisites": [],
                    "learning_objectives": ["Understand digital responsibility", "Practice ethical online behavior"]
                }
            ]
            
            # Apply basic filtering for demo
            if search_criteria.get("category"):
                modules = [m for m in modules if m["category"] == search_criteria["category"]]
            if search_criteria.get("difficulty"):
                modules = [m for m in modules if m["difficulty_level"] == search_criteria["difficulty"]]
            
            return modules, len(modules)
        
        try:
            # In real implementation, this would query Firestore
            return [], 0
        except Exception as e:
            logger.error(f"Error searching learning modules: {str(e)}")
            return [], 0

    async def search_enhanced_learning_modules(self, search_criteria: Dict[str, Any], user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search learning modules with filters."""
        if self.use_mock:
            logger.info("Mock: Returning sample learning modules")
            return [
                {
                    "id": "module_1",
                    "title": "Introduction to Misinformation",
                    "description": "Learn the basics of identifying misinformation and fake news.",
                    "content": "# Introduction to Misinformation\n\nThis module covers the fundamentals of misinformation detection...",
                    "category": "misinformation-awareness",
                    "difficulty_level": "beginner",
                    "estimated_duration_minutes": 30,
                    "tags": ["misinformation", "basics", "detection"],
                    "author_id": "system",
                    "author_name": "MisinfoGuard Team",
                    "is_published": True,
                    "created_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat(),
                    "completion_count": 125,
                    "average_rating": 4.5,
                    "rating_count": 20
                },
                {
                    "id": "module_2",
                    "title": "Spotting Deepfakes",
                    "description": "Advanced techniques for identifying AI-generated media.",
                    "content": "# Spotting Deepfakes\n\nDeepfakes are becoming increasingly sophisticated...",
                    "category": "media-literacy",
                    "difficulty_level": "intermediate",
                    "estimated_duration_minutes": 45,
                    "tags": ["deepfakes", "AI", "video", "image"],
                    "author_id": "system",
                    "author_name": "MisinfoGuard Team",
                    "is_published": True,
                    "created_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat(),
                    "completion_count": 89,
                    "average_rating": 4.7,
                    "rating_count": 15
                },
                {
                    "id": "module_3",
                    "title": "Social Media Fact-Checking",
                    "description": "Tools and techniques for verifying social media content.",
                    "content": "# Social Media Fact-Checking\n\nSocial media is a breeding ground for misinformation...",
                    "category": "fact-checking",
                    "difficulty_level": "beginner",
                    "estimated_duration_minutes": 25,
                    "tags": ["social-media", "verification", "tools"],
                    "author_id": "system", 
                    "author_name": "MisinfoGuard Team",
                    "is_published": True,
                    "created_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat(),
                    "completion_count": 156,
                    "average_rating": 4.3,
                    "rating_count": 25
                },
                {
                    "id": "module_4",
                    "title": "Understanding Bias in News",
                    "description": "How to identify and account for bias in news reporting.",
                    "content": "# Understanding Bias in News\n\nMedia bias can influence how information is presented...",
                    "category": "news-analysis",
                    "difficulty_level": "intermediate",
                    "estimated_duration_minutes": 40,
                    "tags": ["bias", "news", "analysis", "critical-thinking"],
                    "author_id": "system",
                    "author_name": "MisinfoGuard Team",
                    "is_published": True,
                    "created_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat(),
                    "completion_count": 67,
                    "average_rating": 4.4,
                    "rating_count": 12
                },
                {
                    "id": "module_5",
                    "title": "Digital Citizenship Basics",
                    "description": "Responsible behavior and critical thinking in digital spaces.",
                    "content": "# Digital Citizenship Basics\n\nBeing a good digital citizen means...",
                    "category": "digital-citizenship",
                    "difficulty_level": "beginner",
                    "estimated_duration_minutes": 35,
                    "tags": ["digital-citizenship", "responsibility", "ethics"],
                    "author_id": "system",
                    "author_name": "MisinfoGuard Team", 
                    "is_published": True,
                    "created_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat(),
                    "completion_count": 98,
                    "average_rating": 4.6,
                    "rating_count": 18
                }
            ]
        
        try:
            # In real implementation, this would query Firestore
            return []
        except Exception as e:
            logger.error(f"Error searching learning modules: {str(e)}")
            return []

    async def create_enhanced_learning_module(self, module_data: Dict[str, Any]) -> str:
        """Create a new learning module."""
        if self.use_mock:
            import uuid
            module_id = str(uuid.uuid4())
            logger.info(f"Mock: Created learning module {module_id}")
            return module_id
        
        try:
            # In real implementation, this would create in Firestore
            return "mock_module_id"
        except Exception as e:
            logger.error(f"Error creating learning module: {str(e)}")
            raise

    async def get_enhanced_learning_module(self, module_id: str) -> Optional[Dict[str, Any]]:
        """Get a learning module by ID."""
        if self.use_mock:
            logger.info(f"Mock: Getting learning module {module_id}")
            return {
                "id": module_id,
                "title": "Sample Learning Module",
                "description": "This is a sample learning module description...",
                "content": "# Sample Module\n\nThis is sample content for a learning module...",
                "category": "misinformation-awareness",
                "difficulty_level": "beginner",
                "estimated_duration_minutes": 30,
                "tags": ["sample", "test"],
                "author_id": "system",
                "author_name": "System",
                "is_published": True,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "completion_count": 0,
                "average_rating": 0,
                "rating_count": 0
            }
        
        try:
            # In real implementation, this would query Firestore
            return None
        except Exception as e:
            logger.error(f"Error getting learning module: {str(e)}")
            return None

    async def update_enhanced_learning_module(self, module_id: str, update_data: Dict[str, Any]) -> None:
        """Update a learning module."""
        if self.use_mock:
            logger.info(f"Mock: Updated learning module {module_id}")
            return
        
        try:
            # In real implementation, this would update in Firestore
            pass
        except Exception as e:
            logger.error(f"Error updating learning module: {str(e)}")
            raise


# Global instance
firestore_service = FirestoreService()
