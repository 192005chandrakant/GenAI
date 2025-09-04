"""
Learning and educational endpoints for user skill development.
"""
import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from app.models.dto import LearnCard, BaseResponse
from app.models.learning_schemas import (
    Course, Lesson, Quiz, QuizAttempt, Progress, 
    Certificate, LearningPath, InteractiveModule
)
from app.auth.firebase import get_current_user
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


@router.get("/courses", response_model=List[Course])
async def get_courses(
    category: Optional[str] = None,
    difficulty: Optional[str] = None,
    featured: bool = False,
    current_user: dict = Depends(get_current_user)
):
    """Get available learning courses with optional filtering."""
    try:
        user_id = current_user.get("uid") if current_user else None
        
        if settings.use_mocks:
            return [
                Course(
                    id="fact_check_basics",
                    title="Fact-Checking Fundamentals",
                    description="Learn the essential skills of fact-checking and media literacy",
                    category="fundamentals",
                    difficulty="beginner",
                    duration_minutes=120,
                    lesson_count=8,
                    enrolled_count=1234,
                    rating=4.8,
                    thumbnail_url="/images/courses/fact-check-basics.jpg",
                    instructor="Dr. Sarah Truth",
                    featured=True,
                    tags=["fact-checking", "media literacy", "basics"],
                    prerequisites=[],
                    learning_objectives=[
                        "Identify reliable sources",
                        "Recognize common misinformation patterns", 
                        "Apply verification techniques"
                    ],
                    enrolled=bool(user_id),
                    progress_percentage=65 if user_id else 0,
                    certificate_available=True
                ),
                Course(
                    id="advanced_verification",
                    title="Advanced Verification Techniques",
                    description="Master advanced tools and methods for digital investigation",
                    category="advanced",
                    difficulty="intermediate", 
                    duration_minutes=180,
                    lesson_count=12,
                    enrolled_count=567,
                    rating=4.9,
                    thumbnail_url="/images/courses/advanced-verification.jpg",
                    instructor="Prof. Digital Detective",
                    featured=False,
                    tags=["verification", "digital forensics", "investigation"],
                    prerequisites=["fact_check_basics"],
                    learning_objectives=[
                        "Use reverse image search effectively",
                        "Analyze metadata and digital footprints",
                        "Cross-reference multiple sources"
                    ],
                    enrolled=False,
                    progress_percentage=0,
                    certificate_available=True
                )
            ]
        
        courses = await firestore_service.get_courses(
            category=category,
            difficulty=difficulty,
            featured=featured,
            user_id=user_id
        )
        return courses
        
    except Exception as e:
        logger.error(f"Error getting courses: {e}")
        raise HTTPException(status_code=500, detail="Failed to get courses")


@router.get("/courses/{course_id}", response_model=Course)
async def get_course_details(
    course_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get detailed information about a specific course."""
    try:
        user_id = current_user.get("uid") if current_user else None
        
        if settings.use_mocks and course_id == "fact_check_basics":
            return Course(
                id="fact_check_basics",
                title="Fact-Checking Fundamentals",
                description="Learn the essential skills of fact-checking and media literacy. This comprehensive course covers everything from identifying reliable sources to recognizing sophisticated misinformation campaigns.",
                category="fundamentals",
                difficulty="beginner",
                duration_minutes=120,
                lesson_count=8,
                enrolled_count=1234,
                rating=4.8,
                thumbnail_url="/images/courses/fact-check-basics.jpg",
                instructor="Dr. Sarah Truth",
                featured=True,
                tags=["fact-checking", "media literacy", "basics"],
                prerequisites=[],
                learning_objectives=[
                    "Identify reliable and unreliable sources",
                    "Recognize common misinformation patterns and techniques",
                    "Apply systematic verification techniques",
                    "Understand the importance of context in information",
                    "Use fact-checking tools and databases effectively"
                ],
                enrolled=bool(user_id),
                progress_percentage=65 if user_id else 0,
                certificate_available=True
            )
        
        course = await firestore_service.get_course_details(course_id, user_id)
        
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")
        
        return course
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting course details: {e}")
        raise HTTPException(status_code=500, detail="Failed to get course details")


@router.post("/courses/{course_id}/enroll")
async def enroll_in_course(
    course_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Enroll the current user in a course."""
    try:
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        if settings.use_mocks:
            return BaseResponse(
                success=True,
                message=f"Successfully enrolled in course: {course_id}"
            )
        
        result = await firestore_service.enroll_in_course(
            user_id=current_user["uid"],
            course_id=course_id
        )
        
        if not result:
            raise HTTPException(status_code=400, detail="Unable to enroll in course")
        
        return BaseResponse(
            success=True,
            message="Successfully enrolled in course"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error enrolling in course: {e}")
        raise HTTPException(status_code=500, detail="Failed to enroll in course")


@router.get("/courses/{course_id}/lessons", response_model=List[Lesson])
async def get_course_lessons(
    course_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get lessons for a specific course."""
    try:
        user_id = current_user.get("uid") if current_user else None
        
        if settings.use_mocks and course_id == "fact_check_basics":
            return [
                Lesson(
                    id="lesson_001",
                    course_id=course_id,
                    title="Introduction to Fact-Checking",
                    description="Overview of fact-checking principles and why they matter",
                    order=1,
                    duration_minutes=15,
                    lesson_type="video",
                    content_url="/content/lesson_001.mp4",
                    completed=True if user_id else False,
                    locked=False,
                    quiz_required=True,
                    resources=[
                        {"title": "Fact-Checking Guide PDF", "url": "/resources/guide.pdf"},
                        {"title": "Verification Checklist", "url": "/resources/checklist.pdf"}
                    ]
                ),
                Lesson(
                    id="lesson_002", 
                    course_id=course_id,
                    title="Identifying Reliable Sources",
                    description="Learn how to evaluate source credibility and reliability",
                    order=2,
                    duration_minutes=20,
                    lesson_type="interactive",
                    content_url="/content/lesson_002.html",
                    completed=False if user_id else False,
                    locked=False if user_id else True,
                    quiz_required=True,
                    resources=[
                        {"title": "Source Evaluation Worksheet", "url": "/resources/sources.pdf"}
                    ]
                )
            ]
        
        lessons = await firestore_service.get_course_lessons(course_id, user_id)
        return lessons
        
    except Exception as e:
        logger.error(f"Error getting course lessons: {e}")
        raise HTTPException(status_code=500, detail="Failed to get course lessons")


@router.post("/lessons/{lesson_id}/complete")
async def complete_lesson(
    lesson_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Mark a lesson as completed."""
    try:
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        if settings.use_mocks:
            return {
                "success": True,
                "points_earned": 10,
                "message": "Lesson completed successfully!",
                "next_lesson_unlocked": True
            }
        
        result = await firestore_service.complete_lesson(
            user_id=current_user["uid"],
            lesson_id=lesson_id
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error completing lesson: {e}")
        raise HTTPException(status_code=500, detail="Failed to complete lesson")


@router.get("/quizzes/{quiz_id}", response_model=Quiz)
async def get_quiz(
    quiz_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get quiz questions for a lesson."""
    try:
        user_id = current_user.get("uid") if current_user else None
        
        if settings.use_mocks:
            return Quiz(
                id=quiz_id,
                lesson_id="lesson_001",
                title="Fact-Checking Basics Quiz",
                description="Test your understanding of fact-checking fundamentals",
                questions=[
                    {
                        "id": "q1",
                        "question": "What is the first step in fact-checking a claim?",
                        "type": "multiple_choice",
                        "options": [
                            "Share it immediately",
                            "Check the source",
                            "Ignore it completely",
                            "Add your opinion"
                        ],
                        "correct_answer": "Check the source"
                    },
                    {
                        "id": "q2", 
                        "question": "Which of these is a reliable fact-checking website?",
                        "type": "multiple_choice",
                        "options": [
                            "Random blog",
                            "Snopes.com",
                            "Social media post",
                            "Anonymous forum"
                        ],
                        "correct_answer": "Snopes.com"
                    }
                ],
                passing_score=80,
                time_limit_minutes=10,
                attempts_allowed=3,
                attempts_used=1 if user_id else 0
            )
        
        quiz = await firestore_service.get_quiz(quiz_id, user_id)
        
        if not quiz:
            raise HTTPException(status_code=404, detail="Quiz not found")
        
        return quiz
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting quiz: {e}")
        raise HTTPException(status_code=500, detail="Failed to get quiz")


@router.post("/quizzes/{quiz_id}/submit", response_model=QuizAttempt)
async def submit_quiz(
    quiz_id: str,
    answers: dict,
    current_user: dict = Depends(get_current_user)
):
    """Submit quiz answers and get results."""
    try:
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        if settings.use_mocks:
            score = 85  # Mock score
            passed = score >= 80
            
            return QuizAttempt(
                id="attempt_001",
                quiz_id=quiz_id,
                user_id=current_user["uid"],
                answers=answers,
                score=score,
                passed=passed,
                attempt_number=1,
                completed_at="2025-09-04T11:30:00Z",
                time_taken_minutes=8,
                feedback=[
                    {"question_id": "q1", "correct": True, "explanation": "Correct! Always verify the source first."},
                    {"question_id": "q2", "correct": True, "explanation": "Excellent! Snopes is a trusted fact-checking resource."}
                ]
            )
        
        attempt = await firestore_service.submit_quiz(
            quiz_id=quiz_id,
            user_id=current_user["uid"],
            answers=answers
        )
        
        return attempt
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error submitting quiz: {e}")
        raise HTTPException(status_code=500, detail="Failed to submit quiz")


@router.get("/progress", response_model=Progress)
async def get_learning_progress(
    current_user: dict = Depends(get_current_user)
):
    """Get user's overall learning progress."""
    try:
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        if settings.use_mocks:
            return Progress(
                user_id=current_user["uid"],
                courses_enrolled=2,
                courses_completed=1,
                lessons_completed=15,
                quizzes_passed=12,
                certificates_earned=1,
                total_learning_time_minutes=240,
                current_streak_days=5,
                learning_points=850,
                skill_levels={
                    "fact_checking": 3,
                    "source_verification": 2,
                    "digital_literacy": 4
                },
                recent_activity=[
                    {
                        "type": "lesson_completed",
                        "title": "Advanced Source Verification",
                        "timestamp": "2025-09-04T10:30:00Z",
                        "points_earned": 15
                    },
                    {
                        "type": "quiz_passed", 
                        "title": "Media Literacy Quiz",
                        "timestamp": "2025-09-03T16:45:00Z",
                        "points_earned": 25
                    }
                ]
            )
        
        progress = await firestore_service.get_learning_progress(current_user["uid"])
        return progress
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting learning progress: {e}")
        raise HTTPException(status_code=500, detail="Failed to get learning progress")


@router.get("/certificates", response_model=List[Certificate])
async def get_user_certificates(
    current_user: dict = Depends(get_current_user)
):
    """Get certificates earned by the user."""
    try:
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        if settings.use_mocks:
            return [
                Certificate(
                    id="cert_001",
                    user_id=current_user["uid"],
                    course_id="fact_check_basics",
                    course_title="Fact-Checking Fundamentals",
                    issued_at="2025-09-01T00:00:00Z",
                    certificate_url="/certificates/cert_001.pdf",
                    verification_code="FC-2025-001-ABC123",
                    skills_validated=[
                        "Source evaluation",
                        "Information verification",
                        "Media literacy fundamentals"
                    ]
                )
            ]
        
        certificates = await firestore_service.get_user_certificates(current_user["uid"])
        return certificates
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting certificates: {e}")
        raise HTTPException(status_code=500, detail="Failed to get certificates")


@router.get("/paths", response_model=List[LearningPath])
async def get_learning_paths(
    current_user: dict = Depends(get_current_user)
):
    """Get recommended learning paths for the user."""
    try:
        user_id = current_user.get("uid") if current_user else None
        
        if settings.use_mocks:
            return [
                LearningPath(
                    id="beginner_path",
                    title="Beginner Fact-Checker",
                    description="Complete learning path for newcomers to fact-checking",
                    difficulty="beginner",
                    estimated_duration_hours=6,
                    course_ids=["fact_check_basics", "source_evaluation"],
                    prerequisites=[],
                    skills_gained=["Basic verification", "Source assessment", "Critical thinking"],
                    completion_rate=45 if user_id else 0,
                    enrolled=bool(user_id)
                ),
                LearningPath(
                    id="expert_path",
                    title="Digital Investigation Expert",
                    description="Advanced path for professional fact-checkers and investigators",
                    difficulty="advanced",
                    estimated_duration_hours=15,
                    course_ids=["advanced_verification", "digital_forensics", "investigation_techniques"],
                    prerequisites=["fact_check_basics"],
                    skills_gained=["Digital forensics", "Advanced verification", "Investigation methods"],
                    completion_rate=0,
                    enrolled=False
                )
            ]
        
        paths = await firestore_service.get_learning_paths(user_id)
        return paths
        
    except Exception as e:
        logger.error(f"Error getting learning paths: {e}")
        raise HTTPException(status_code=500, detail="Failed to get learning paths")


@router.get("/interactive/{module_id}", response_model=InteractiveModule)
async def get_interactive_module(
    module_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get interactive learning module content."""
    try:
        if settings.use_mocks:
            return InteractiveModule(
                id=module_id,
                title="Interactive Source Analysis",
                description="Practice evaluating different types of sources",
                module_type="simulation",
                content={
                    "scenario": "You encounter a news article about a scientific breakthrough. Analyze its credibility.",
                    "article_url": "https://example.com/article",
                    "evaluation_criteria": [
                        "Source authority",
                        "Evidence quality", 
                        "Peer review status",
                        "Publication date"
                    ],
                    "tools_available": ["reverse_search", "domain_checker", "citation_tracker"]
                },
                completion_criteria={
                    "min_checks": 5,
                    "accuracy_threshold": 80
                },
                rewards={
                    "points": 50,
                    "badge": "source_analyst"
                },
                estimated_duration_minutes=25
            )
        
        module = await firestore_service.get_interactive_module(module_id)
        
        if not module:
            raise HTTPException(status_code=404, detail="Interactive module not found")
        
        return module
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting interactive module: {e}")
        raise HTTPException(status_code=500, detail="Failed to get interactive module")


@router.post("/interactive/{module_id}/submit")
async def submit_interactive_module(
    module_id: str,
    submission: dict,
    current_user: dict = Depends(get_current_user)
):
    """Submit interactive module completion."""
    try:
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        if settings.use_mocks:
            return {
                "success": True,
                "score": 85,
                "points_earned": 50,
                "badge_earned": "source_analyst",
                "feedback": "Excellent analysis! You correctly identified the key credibility factors.",
                "next_module": "advanced_verification_sim"
            }
        
        result = await firestore_service.submit_interactive_module(
            module_id=module_id,
            user_id=current_user["uid"],
            submission=submission
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error submitting interactive module: {e}")
        raise HTTPException(status_code=500, detail="Failed to submit interactive module")
