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
        try:
            if settings.use_mocks or settings.google_cloud_project == "local-gcp-project":
                logger.info("Using mock Firestore service")
                self.use_mock = True
                self.db = None
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


# Global instance
firestore_service = FirestoreService()
