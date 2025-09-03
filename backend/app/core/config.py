"""
Configuration settings for the Misinformation Detection API.
"""
from pydantic import Field
from pydantic_settings import BaseSettings
from typing import Optional, List
import os


class Settings(BaseSettings):
    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Misinformation Detection Platform"
    VERSION: str = "1.0.0"
    DEBUG: bool = Field(default=False, env="DEBUG")
    
    # Server Configuration
    HOST: str = Field(default="0.0.0.0", env="HOST")
    PORT: int = Field(default=8000, env="PORT")
    RELOAD: bool = Field(default=False, env="RELOAD")
    
    # Google Cloud Configuration
    GOOGLE_CLOUD_PROJECT: Optional[str] = Field(
        default="local-gcp-project",
        env="GOOGLE_CLOUD_PROJECT",
        description="Google Cloud project ID (optional for local dev)"
    )
    GOOGLE_APPLICATION_CREDENTIALS: Optional[str] = Field(None, env="GOOGLE_APPLICATION_CREDENTIALS")

    # Vertex AI Configuration
    VERTEX_AI_LOCATION: str = Field(default="us-central1", env="VERTEX_AI_LOCATION")
    VERTEX_AI_MODEL_GEMINI_FLASH: str = Field(default="gemini-1.5-flash", env="VERTEX_AI_MODEL_GEMINI_FLASH")
    VERTEX_AI_MODEL_GEMINI_PRO: str = Field(default="gemini-1.5-pro", env="VERTEX_AI_MODEL_GEMINI_PRO")
    VERTEX_AI_MODEL_EMBEDDING: str = Field(default="textembedding-gecko@003", env="VERTEX_AI_MODEL_EMBEDDING")

    # Firebase Configuration
    FIREBASE_PROJECT_ID: Optional[str] = Field(default="local-firebase-project", env="FIREBASE_PROJECT_ID")
    FIREBASE_PRIVATE_KEY_ID: Optional[str] = Field(default="local-key-id", env="FIREBASE_PRIVATE_KEY_ID")
    FIREBASE_PRIVATE_KEY: Optional[str] = Field(default="local-private-key", env="FIREBASE_PRIVATE_KEY")
    FIREBASE_CLIENT_EMAIL: Optional[str] = Field(default="local-client-email", env="FIREBASE_CLIENT_EMAIL")
    FIREBASE_CLIENT_ID: Optional[str] = Field(default="local-client-id", env="FIREBASE_CLIENT_ID")
    FIREBASE_AUTH_DOMAIN: Optional[str] = Field(default="localhost", env="FIREBASE_AUTH_DOMAIN")

    # Firestore Configuration
    FIRESTORE_COLLECTION_CHECKS: str = Field(default="checks", env="FIRESTORE_COLLECTION_CHECKS")

    # Cloud Storage
    CLOUD_STORAGE_BUCKET: Optional[str] = Field(default="local-bucket", env="CLOUD_STORAGE_BUCKET")

    # Secret Manager
    SECRET_MANAGER_PROJECT_ID: Optional[str] = Field(default="local-secret-project", env="SECRET_MANAGER_PROJECT_ID")

    # Fact Check API
    FACT_CHECK_API_KEY: Optional[str] = Field(default="local-fact-check-key", env="FACT_CHECK_API_KEY")

    # JWT Secret
    JWT_SECRET_KEY: Optional[str] = Field(default="local-jwt-secret", env="JWT_SECRET_KEY")

    def require_production_vars(self):
        if not self.DEBUG:
            required_vars = [
                self.GOOGLE_CLOUD_PROJECT,
                self.FIREBASE_PROJECT_ID,
                self.FIREBASE_PRIVATE_KEY_ID,
                self.FIREBASE_PRIVATE_KEY,
                self.FIREBASE_CLIENT_EMAIL,
                self.FIREBASE_CLIENT_ID,
                self.FIREBASE_AUTH_DOMAIN,
                self.CLOUD_STORAGE_BUCKET,
                self.SECRET_MANAGER_PROJECT_ID,
                self.FACT_CHECK_API_KEY,
                self.JWT_SECRET_KEY,
            ]
            missing = [v for v in required_vars if not v or v.startswith('local-') or v == 'localhost']
            if missing:
                raise ValueError(f"Missing required environment variables for production: {missing}")
    FIRESTORE_COLLECTION_SOURCES: str = Field(default="sources", env="FIRESTORE_COLLECTION_SOURCES")
    FIRESTORE_COLLECTION_LESSONS: str = Field(default="lessons", env="FIRESTORE_COLLECTION_LESSONS")
    FIRESTORE_COLLECTION_USERS: str = Field(default="users", env="FIRESTORE_COLLECTION_USERS")
    FIRESTORE_COLLECTION_REPORTS: str = Field(default="reports", env="FIRESTORE_COLLECTION_REPORTS")
    
    # BigQuery Configuration
    BIGQUERY_DATASET: str = Field(default="misinformation_analytics", env="BIGQUERY_DATASET")
    BIGQUERY_TABLE_CHECKS: str = Field(default="checks", env="BIGQUERY_TABLE_CHECKS")
    BIGQUERY_TABLE_USERS: str = Field(default="users", env="BIGQUERY_TABLE_USERS")
    BIGQUERY_TABLE_ANALYTICS: str = Field(default="analytics", env="BIGQUERY_TABLE_ANALYTICS")
    
    # Cloud Storage Configuration
    CLOUD_STORAGE_BUCKET: Optional[str] = Field(default="local-bucket", env="CLOUD_STORAGE_BUCKET")
    CLOUD_STORAGE_MAX_FILE_SIZE: int = Field(default=10 * 1024 * 1024, env="CLOUD_STORAGE_MAX_FILE_SIZE")  # 10MB
    CLOUD_STORAGE_ALLOWED_EXTENSIONS: List[str] = Field(default=["jpg", "jpeg", "png", "gif", "mp4", "avi", "mov"], env="CLOUD_STORAGE_ALLOWED_EXTENSIONS")
    MAX_FILE_SIZE: int = Field(default=10485760, env="MAX_FILE_SIZE")

    # API Keys
    GEMINI_API_KEY: Optional[str] = Field(default="local-gemini-key", env="GEMINI_API_KEY")
    TRANSLATE_API_KEY: Optional[str] = Field(default="local-translate-key", env="TRANSLATE_API_KEY")

    # Firestore Configuration
    FIRESTORE_COLLECTION: str = Field(default="misinformation_reports", env="FIRESTORE_COLLECTION")
    FIRESTORE_COLLECTION_CHECKS: str = Field(default="checks", env="FIRESTORE_COLLECTION_CHECKS")
    FIRESTORE_COLLECTION_REPORTS: str = Field(default="reports", env="FIRESTORE_COLLECTION_REPORTS")

    # Authentication Algorithm
    ALGORITHM: str = Field(default="HS256", env="ALGORITHM")

    # CORS Origins as string (will be parsed)
    ALLOWED_ORIGINS: str = Field(default='["http://localhost:3000","http://localhost:3001"]', env="ALLOWED_ORIGINS")

    # Gemini Models
    GEMINI_MODEL: str = Field(default="gemini-pro", env="GEMINI_MODEL")
    GEMINI_VISION_MODEL: str = Field(default="gemini-pro-vision", env="GEMINI_VISION_MODEL")

    # Gamification Points
    POINTS_PER_REPORT: int = Field(default=10, env="POINTS_PER_REPORT")
    POINTS_PER_CORRECT_DETECTION: int = Field(default=5, env="POINTS_PER_CORRECT_DETECTION")
    POINTS_PER_LEARNING_MODULE: int = Field(default=3, env="POINTS_PER_LEARNING_MODULE")
    
    # Pub/Sub Configuration
    PUBSUB_TOPIC_CONTENT_ANALYSIS: str = Field(default="content-analysis", env="PUBSUB_TOPIC_CONTENT_ANALYSIS")
    PUBSUB_SUBSCRIPTION_CONTENT_ANALYSIS: str = Field(default="content-analysis-sub", env="PUBSUB_SUBSCRIPTION_CONTENT_ANALYSIS")
    PUBSUB_TOPIC_BATCH_PROCESSING: str = Field(default="batch-processing", env="PUBSUB_TOPIC_BATCH_PROCESSING")
    
    # Cloud Scheduler Configuration
    CLOUD_SCHEDULER_BATCH_INDEX_REFRESH: str = Field(default="batch-index-refresh", env="CLOUD_SCHEDULER_BATCH_INDEX_REFRESH")
    CLOUD_SCHEDULER_CRON_BATCH_INDEX: str = Field(default="0 2 * * *", env="CLOUD_SCHEDULER_CRON_BATCH_INDEX")  # Daily at 2 AM
    
    # Secret Manager Configuration
    SECRET_MANAGER_PROJECT_ID: Optional[str] = Field(default="local-secret-project", env="SECRET_MANAGER_PROJECT_ID")
    
    # Fact Check Tools API
    FACT_CHECK_API_KEY: Optional[str] = Field(default="local-fact-check-key", env="FACT_CHECK_API_KEY")
    FACT_CHECK_API_URL: str = Field(default="https://factchecktools.googleapis.com/v1alpha1/claims:search", env="FACT_CHECK_API_URL")
    
    # RSS Feeds Configuration
    RSS_FEEDS: List[str] = Field(default=[
        "https://www.snopes.com/feed/",
        "https://www.factcheck.org/feed/",
        "https://www.politifact.com/feed/",
        "https://www.reuters.com/tools/rss",
        "https://www.bbc.com/news/rss.xml"
    ], env="RSS_FEEDS")
    
    # FAISS Configuration
    FAISS_INDEX_PATH: str = Field(default="/tmp/faiss_index", env="FAISS_INDEX_PATH")
    FAISS_DIMENSION: int = Field(default=768, env="FAISS_DIMENSION")  # Gecko embedding dimension
    FAISS_NPROBE: int = Field(default=10, env="FAISS_NPROBE")
    
    # Media Processing Configuration
    TESSERACT_CMD: str = Field(default="/usr/bin/tesseract", env="TESSERACT_CMD")
    EXIFTOOL_PATH: str = Field(default="/usr/bin/exiftool", env="EXIFTOOL_PATH")
    FFMPEG_PATH: str = Field(default="/usr/bin/ffmpeg", env="FFMPEG_PATH")
    
    # ONNX Model Configuration
    ONNX_MODEL_PATH: str = Field(default="/app/models/stance_classifier.onnx", env="ONNX_MODEL_PATH")
    ONNX_MODEL_THRESHOLD: float = Field(default=0.7, env="ONNX_MODEL_THRESHOLD")
    
    # Authentication Configuration
    JWT_SECRET_KEY: Optional[str] = Field(default="local-jwt-secret", env="JWT_SECRET_KEY")
    JWT_ALGORITHM: str = Field(default="HS256", env="JWT_ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7, env="REFRESH_TOKEN_EXPIRE_DAYS")
    
    # CORS Configuration
    CORS_ORIGINS: List[str] = Field(default=["http://localhost:3000", "https://localhost:3000"], env="CORS_ORIGINS")
    CORS_ALLOW_CREDENTIALS: bool = Field(default=True, env="CORS_ALLOW_CREDENTIALS")
    CORS_ALLOW_METHODS: List[str] = Field(default=["*"], env="CORS_ALLOW_METHODS")
    CORS_ALLOW_HEADERS: List[str] = Field(default=["*"], env="CORS_ALLOW_HEADERS")
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = Field(default=60, env="RATE_LIMIT_PER_MINUTE")
    RATE_LIMIT_PER_HOUR: int = Field(default=1000, env="RATE_LIMIT_PER_HOUR")
    
    # Redis Configuration
    REDIS_URL: str = Field(default="redis://localhost:6379", env="REDIS_URL")
    REDIS_DB: int = Field(default=0, env="REDIS_DB")
    REDIS_PASSWORD: Optional[str] = Field(None, env="REDIS_PASSWORD")
    
    # Celery Configuration
    CELERY_BROKER_URL: str = Field(default="redis://localhost:6379/1", env="CELERY_BROKER_URL")
    CELERY_RESULT_BACKEND: str = Field(default="redis://localhost:6379/2", env="CELERY_RESULT_BACKEND")
    
    # Logging Configuration
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_FORMAT: str = Field(default="json", env="LOG_FORMAT")
    
    # Performance Configuration
    MAX_CONCURRENT_REQUESTS: int = Field(default=100, env="MAX_CONCURRENT_REQUESTS")
    REQUEST_TIMEOUT: int = Field(default=30, env="REQUEST_TIMEOUT")
    
    # AI Model Configuration
    AI_MODEL_DEFAULT: str = Field(default="flash", env="AI_MODEL_DEFAULT")  # flash or pro
    AI_MODEL_ESCALATION_THRESHOLD: float = Field(default=0.8, env="AI_MODEL_ESCALATION_THRESHOLD")
    AI_MODEL_MAX_TOKENS: int = Field(default=4096, env="AI_MODEL_MAX_TOKENS")
    AI_MODEL_TEMPERATURE: float = Field(default=0.1, env="AI_MODEL_TEMPERATURE")
    
    # Gamification Configuration
    POINTS_ANALYSIS: int = Field(default=10, env="POINTS_ANALYSIS")
    POINTS_REPORT: int = Field(default=20, env="POINTS_REPORT")
    POINTS_LEARNING: int = Field(default=5, env="POINTS_LEARNING")
    POINTS_ACHIEVEMENT: int = Field(default=50, env="POINTS_ACHIEVEMENT")
    
    # Privacy Configuration
    DATA_RETENTION_DAYS: int = Field(default=90, env="DATA_RETENTION_DAYS")
    ANONYMIZE_ANALYTICS: bool = Field(default=True, env="ANONYMIZE_ANALYTICS")
    OPT_IN_TELEMETRY: bool = Field(default=False, env="OPT_IN_TELEMETRY")
    
    # Multilingual Configuration
    SUPPORTED_LANGUAGES: List[str] = Field(default=["en", "hi", "bn", "te", "ta", "mr", "kn"], env="SUPPORTED_LANGUAGES")
    DEFAULT_LANGUAGE: str = Field(default="en", env="DEFAULT_LANGUAGE")
    
    # Evaluation Configuration
    EVALUATION_ENABLED: bool = Field(default=True, env="EVALUATION_ENABLED")
    A_B_TESTING_ENABLED: bool = Field(default=False, env="A_B_TESTING_ENABLED")
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
