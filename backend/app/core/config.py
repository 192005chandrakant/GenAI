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
    
    # Development Configuration
    USE_MOCKS: bool = Field(default=True, env="USE_MOCKS")
    
    # Server Configuration
    HOST: str = Field(default="0.0.0.0", env="HOST")
    PORT: int = Field(default=8000, env="PORT")
    RELOAD: bool = Field(default=False, env="RELOAD")
    
    # Google Cloud Configuration
    GOOGLE_CLOUD_PROJECT: Optional[str] = Field(
        default="local-gcp-project",
        env="GOOGLE_PROJECT_ID",  # Changed to match the .env file
        description="Google Cloud project ID (optional for local dev)"
    )
    GOOGLE_APPLICATION_CREDENTIALS: Optional[str] = Field(None, env="GOOGLE_APPLICATION_CREDENTIALS")

    # Vertex AI Configuration
    VERTEX_AI_LOCATION: str = Field(default="us-central1", env="VERTEX_AI_LOCATION")
    VERTEX_AI_MODEL_GEMINI_FLASH: str = Field(default="gemini-1.5-flash", env="VERTEX_AI_MODEL_GEMINI_FLASH")
    VERTEX_AI_MODEL_GEMINI_PRO: str = Field(default="gemini-1.5-pro", env="VERTEX_AI_MODEL_GEMINI_PRO")
    VERTEX_AI_MODEL_EMBEDDING: str = Field(default="textembedding-gecko@003", env="VERTEX_AI_MODEL_EMBEDDING")
    
    # AI Model Configuration
    AI_MODEL_DEFAULT: str = Field(default="gemini-flash", env="AI_MODEL_DEFAULT")
    AI_MODEL_ESCALATION_THRESHOLD: float = Field(default=0.7, env="AI_MODEL_ESCALATION_THRESHOLD")
    AI_MODEL_MAX_TOKENS: int = Field(default=2048, env="AI_MODEL_MAX_TOKENS")
    AI_MODEL_TEMPERATURE: float = Field(default=0.1, env="AI_MODEL_TEMPERATURE")
    
    # FAISS Configuration
    FAISS_INDEX_PATH: str = Field(default="./data/faiss_index", env="FAISS_INDEX_PATH")
    FAISS_DIMENSION: int = Field(default=768, env="FAISS_DIMENSION")
    FAISS_NPROBE: int = Field(default=16, env="FAISS_NPROBE")
    FAISS_BATCH_SIZE: int = Field(default=100, env="FAISS_BATCH_SIZE")

    # Firebase Configuration
    FIREBASE_PROJECT_ID: Optional[str] = Field(default="local-firebase-project", env="FIREBASE_PROJECT_ID")
    FIREBASE_PRIVATE_KEY_ID: Optional[str] = Field(default="local-key-id", env="FIREBASE_PRIVATE_KEY_ID")
    FIREBASE_PRIVATE_KEY: Optional[str] = Field(default="local-private-key", env="FIREBASE_PRIVATE_KEY")
    FIREBASE_CLIENT_EMAIL: Optional[str] = Field(default="local-client-email", env="FIREBASE_CLIENT_EMAIL")
    FIREBASE_CLIENT_ID: Optional[str] = Field(default="local-client-id", env="FIREBASE_CLIENT_ID")
    FIREBASE_AUTH_DOMAIN: Optional[str] = Field(default="localhost", env="FIREBASE_AUTH_DOMAIN")
    
    # OAuth Configuration
    GITHUB_CLIENT_ID: Optional[str] = Field(default="", env="GITHUB_CLIENT_ID")
    GITHUB_CLIENT_SECRET: Optional[str] = Field(default="", env="GITHUB_CLIENT_SECRET")
    GITHUB_CALLBACK_URL: Optional[str] = Field(default="http://localhost:3001/api/auth/callback/github", env="GITHUB_CALLBACK_URL")

    # Cloudinary Configuration
    CLOUDINARY_CLOUD_NAME: Optional[str] = Field(default="", env="CLOUDINARY_CLOUD_NAME")
    CLOUDINARY_API_KEY: Optional[str] = Field(default="", env="CLOUDINARY_API_KEY")
    CLOUDINARY_API_SECRET: Optional[str] = Field(default="", env="CLOUDINARY_API_SECRET")

    # Firestore Configuration
    FIRESTORE_COLLECTION_CHECKS: str = Field(default="checks", env="FIRESTORE_COLLECTION_CHECKS")

    # Cloud Storage Configuration
    CLOUD_STORAGE_BUCKET: Optional[str] = Field(default="local-bucket", env="CLOUD_STORAGE_BUCKET")
    CLOUD_STORAGE_MAX_FILE_SIZE: int = Field(default=10 * 1024 * 1024, env="CLOUD_STORAGE_MAX_FILE_SIZE")  # 10MB
    CLOUD_STORAGE_ALLOWED_EXTENSIONS: List[str] = Field(default=["jpg", "jpeg", "png", "gif", "mp4", "avi", "mov"], env="CLOUD_STORAGE_ALLOWED_EXTENSIONS")
    MAX_FILE_SIZE: int = Field(default=10485760, env="MAX_FILE_SIZE")

    # Firestore Configuration
    FIRESTORE_COLLECTION_SOURCES: str = Field(default="sources", env="FIRESTORE_COLLECTION_SOURCES")
    FIRESTORE_COLLECTION_LESSONS: str = Field(default="lessons", env="FIRESTORE_COLLECTION_LESSONS")
    FIRESTORE_COLLECTION_USERS: str = Field(default="users", env="FIRESTORE_COLLECTION_USERS")
    FIRESTORE_COLLECTION_REPORTS: str = Field(default="reports", env="FIRESTORE_COLLECTION_REPORTS")
    FIRESTORE_COLLECTION_CHECKS: str = Field(default="checks", env="FIRESTORE_COLLECTION_CHECKS")
    
    # BigQuery Configuration
    BIGQUERY_DATASET: str = Field(default="misinformation_analytics", env="BIGQUERY_DATASET")
    BIGQUERY_TABLE_CHECKS: str = Field(default="checks", env="BIGQUERY_TABLE_CHECKS")
    BIGQUERY_TABLE_USERS: str = Field(default="users", env="BIGQUERY_TABLE_USERS")
    BIGQUERY_TABLE_ANALYTICS: str = Field(default="analytics", env="BIGQUERY_TABLE_ANALYTICS")
    # API Keys
    GEMINI_API_KEY: Optional[str] = Field(default="local-gemini-key", env="GEMINI_API_KEY")
    TRANSLATE_API_KEY: Optional[str] = Field(default="local-translate-key", env="TRANSLATE_API_KEY")
    FACT_CHECK_API_KEY: Optional[str] = Field(default="local-fact-check-key", env="FACT_CHECK_API_KEY")

    # Authentication Configuration
    JWT_SECRET_KEY: Optional[str] = Field(default="local-jwt-secret", env="JWT_SECRET_KEY")
    JWT_ALGORITHM: str = Field(default="HS256", env="JWT_ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7, env="REFRESH_TOKEN_EXPIRE_DAYS")
    ALGORITHM: str = Field(default="HS256", env="ALGORITHM")  # Backward compatibility

    # CORS Configuration
    ALLOWED_ORIGINS: str = Field(default='["http://localhost:3000","http://localhost:3001"]', env="ALLOWED_ORIGINS")
    CORS_ORIGINS: List[str] = Field(default=["http://localhost:3000", "https://localhost:3000"], env="CORS_ORIGINS")
    CORS_ALLOW_CREDENTIALS: bool = Field(default=True, env="CORS_ALLOW_CREDENTIALS")
    CORS_ALLOW_METHODS: List[str] = Field(default=["*"], env="CORS_ALLOW_METHODS")
    CORS_ALLOW_HEADERS: List[str] = Field(default=["*"], env="CORS_ALLOW_HEADERS")

    # Gemini Models
    GEMINI_MODEL: str = Field(default="gemini-pro", env="GEMINI_MODEL")
    GEMINI_VISION_MODEL: str = Field(default="gemini-pro-vision", env="GEMINI_VISION_MODEL")

    # Secret Manager Configuration
    SECRET_MANAGER_PROJECT_ID: Optional[str] = Field(default="local-secret-project", env="SECRET_MANAGER_PROJECT_ID")
    # Gamification Configuration
    POINTS_PER_REPORT: int = Field(default=10, env="POINTS_PER_REPORT")
    POINTS_PER_CORRECT_DETECTION: int = Field(default=5, env="POINTS_PER_CORRECT_DETECTION")
    POINTS_PER_LEARNING_MODULE: int = Field(default=3, env="POINTS_PER_LEARNING_MODULE")
    POINTS_ANALYSIS: int = Field(default=10, env="POINTS_ANALYSIS")
    POINTS_REPORT: int = Field(default=20, env="POINTS_REPORT")
    POINTS_LEARNING: int = Field(default=5, env="POINTS_LEARNING")
    POINTS_ACHIEVEMENT: int = Field(default=50, env="POINTS_ACHIEVEMENT")

    # Logging Configuration
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"  # Allow extra fields to handle different variable names

    @property
    def use_mocks(self) -> bool:
        """Property to access USE_MOCKS for backward compatibility."""
        return self.USE_MOCKS

    @property
    def allowed_origins(self) -> List[str]:
        """Parse ALLOWED_ORIGINS string to list."""
        import json
        try:
            return json.loads(self.ALLOWED_ORIGINS)
        except:
            return ["http://localhost:3000", "http://localhost:3001"]

    @property
    def api_v1_str(self) -> str:
        """Property to access API_V1_STR."""
        return self.API_V1_STR

    @property
    def project_name(self) -> str:
        """Property to access PROJECT_NAME."""
        return self.PROJECT_NAME

    @property
    def version(self) -> str:
        """Property to access VERSION."""
        return self.VERSION

    @property
    def host(self) -> str:
        """Property to access HOST."""
        return self.HOST

    @property
    def port(self) -> int:
        """Property to access PORT."""
        return self.PORT

    @property
    def debug(self) -> bool:
        """Property to access DEBUG."""
        return self.DEBUG

    @property
    def google_cloud_project(self) -> Optional[str]:
        """Property to access GOOGLE_CLOUD_PROJECT."""
        return self.GOOGLE_CLOUD_PROJECT


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Compatibility helper used across the codebase.

    Many modules import `get_settings()` (older pattern). Keep a simple
    helper that returns the global `settings` instance to avoid
    ImportError and maintain backward compatibility.
    """
    return settings
