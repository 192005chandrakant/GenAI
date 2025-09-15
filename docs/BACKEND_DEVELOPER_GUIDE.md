# GenAI Backend Developer Guide

This comprehensive guide provides detailed information for backend developers working on the GenAI Misinformation Defense Platform. It covers architecture, API endpoints, services, and development best practices.

## 🏗️ Backend Architecture

### Core Components

```
backend/
├── main.py              # Main FastAPI application entry point
├── simple_main.py       # Simplified version for testing
├── requirements.txt     # Production dependencies
├── app/
│   ├── __init__.py
│   ├── api/             # API endpoints
│   ├── auth/            # Authentication handlers
│   ├── core/            # Core configuration
│   ├── models/          # Data models and schemas
│   └── services/        # Business logic and external services
```

### Service Organization

The backend follows a layered architecture:

1. **API Layer** (`app/api/`) - FastAPI route definitions and handlers
2. **Service Layer** (`app/services/`) - Business logic and external service integration
3. **Model Layer** (`app/models/`) - Data models, validation schemas, and database interfaces
4. **Core Layer** (`app/core/`) - Configuration, dependencies, and application setup

## 🚀 Development Environment

### Prerequisites

- Python 3.11+
- Virtual environment tool (venv, conda, etc.)
- Access to GCP or mock services enabled

### Local Setup

For a minimal setup with mock services:

```bash
# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux

# Install minimal dependencies
pip install -r minimal_requirements.txt

# Configure environment
cp env.example .env
# Edit .env with your settings (USE_MOCKS=True for local dev)

# Run the server
uvicorn main:app --reload
```

### Working with Mock Services

The backend supports development with mock services when `USE_MOCKS=True`:

- **Firestore**: In-memory storage emulation
- **Vertex AI**: Predetermined responses
- **FAISS**: Simplified vector search
- **Authentication**: Mock JWT tokens

This allows development without setting up real GCP services.

## 📊 Backend Dashboard

The backend includes a comprehensive monitoring dashboard:

### Dashboard Features
- **URL**: `http://127.0.0.1:8006/`
- **Real-time Metrics**: CPU, memory, requests, etc.
- **Service Health**: Status of all backend services
- **Request Analytics**: Traffic analysis and performance
- **System Information**: Environment and platform details

### Access Documentation
- **API Portal**: `http://127.0.0.1:8006/api/v1/docs-api/`
- **Swagger UI**: `http://127.0.0.1:8006/docs`
- **ReDoc**: `http://127.0.0.1:8006/redoc`

## 🔧 Backend Services

### AI Services

#### Gemini Service
The `gemini_service.py` provides advanced language model capabilities:
- Text understanding and generation
- Claim extraction
- Entity recognition
- Reasoning and analysis

```python
from app.services.gemini_service import GeminiService

gemini = GeminiService()
result = await gemini.analyze_text("This is a claim to analyze")
```

#### FAISS Service
The `faiss_service.py` provides vector similarity search:
- Document embedding
- Semantic search
- Similar document retrieval
- Document clustering

```python
from app.services.faiss_service import FAISSService

faiss = FAISSService()
similar_docs = await faiss.find_similar("query text", top_k=5)
```

### External Data Services

#### Fact Check Service
The `fact_check_service.py` integrates with fact-checking APIs:
- Google Fact Check Tools API
- Trusted fact-checker databases
- Claim matching

```python
from app.services.fact_check_service import FactCheckService

fact_check = FactCheckService()
matches = await fact_check.find_matches("claim text")
```

#### Translation Service
The `translation_service.py` provides multilingual capabilities:
- Language detection
- Text translation
- Cross-lingual search

```python
from app.services.translation_service import TranslationService

translator = TranslationService()
translated = await translator.translate("Text to translate", target="hi")
```

### Storage Services

#### Firestore Service
The `firestore_service.py` handles database operations:
- CRUD operations
- Query building
- Data validation
- Transaction support

```python
from app.services.firestore_service import FirestoreService

db = FirestoreService()
user = await db.get_document("users", user_id)
```

#### Media Service
The `media_service.py` manages media content:
- Image/video processing
- Cloud storage upload/download
- Media analysis

```python
from app.services.media_service import MediaService

media = MediaService()
result = await media.analyze_image(image_bytes)
```

## 🔐 Authentication

### Firebase Authentication
The backend uses Firebase for authentication:

```python
from app.auth.firebase import verify_firebase_token

# In an endpoint
async def protected_endpoint(token: str = Depends(oauth2_scheme)):
    user = await verify_firebase_token(token)
    # Access user.uid, user.email, etc.
```

### JWT Authentication
For local development or when Firebase is not available:

```python
from app.core.security import create_access_token, verify_access_token

# Create token
token = create_access_token({"sub": user_id})

# Verify token
payload = verify_access_token(token)
```

## 📝 API Models

### Request Models
Define request validation using Pydantic:

```python
from pydantic import BaseModel, Field

class FactCheckRequest(BaseModel):
    input_type: str = Field(..., description="Type of input: text, url, image")
    payload: str = Field(..., description="Content to analyze")
    language: str = Field("auto", description="Content language or 'auto'")
```

### Response Models
Define standardized response formats:

```python
class FactCheckResponse(BaseModel):
    id: str = Field(..., description="Unique check ID")
    score: int = Field(..., ge=0, le=100, description="Credibility score (0-100)")
    verdict: str = Field(..., description="Human-readable verdict")
    claims: list[ClaimModel] = Field([], description="Extracted claims")
    citations: list[CitationModel] = Field([], description="Supporting citations")
```

## 🧪 Testing

### Unit Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_fact_check_service.py
```

### Mock Test Data
The `tests/` directory contains fixtures and mock data for testing.

### Integration Tests
Integration tests verify the interaction between components:

```bash
# Run integration tests
pytest tests/integration/
```

## 🚀 Performance Optimization

### Best Practices

1. **Async Operations**: Use `async/await` for I/O-bound operations
2. **Connection Pooling**: Reuse connections to external services
3. **Caching**: Implement caching for expensive operations
4. **Rate Limiting**: Apply rate limits for external API calls
5. **Background Tasks**: Use FastAPI background tasks for non-critical operations

### Monitoring Performance

The dashboard provides real-time performance metrics:
- Response times
- Request throughput
- Resource utilization
- Error rates

## 📦 Dependency Management

### Adding New Dependencies

```bash
# Add to requirements.txt
pip install new-package
pip freeze > requirements.txt

# For development only
pip install -e new-package
# Add to setup.py or requirements-dev.txt
```

### Managing Environment Variables

Store configuration in `.env` file:
```
# Service configuration
DEBUG=True
PORT=8000
USE_MOCKS=True

# API Keys (mock values shown)
GEMINI_API_KEY=mock-key
FACT_CHECK_API_KEY=mock-key
```

Load environment variables in `app/core/config.py`:
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DEBUG: bool = False
    PORT: int = 8000
    USE_MOCKS: bool = False
    # ... other settings

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
```

## 🚀 Deployment

### Preparing for Deployment

1. **Disable Debug Mode**:
   ```
   DEBUG=False
   USE_MOCKS=False
   ```

2. **Set Production Credentials**:
   - Use production GCP credentials
   - Configure production Firebase project
   - Set production API keys

3. **Build Docker Image**:
   ```bash
   docker build -t genai-backend .
   ```

### Cloud Run Deployment

```bash
# Deploy to Cloud Run
gcloud run deploy genai-backend \
  --image gcr.io/your-project/genai-backend \
  --platform managed \
  --allow-unauthenticated \
  --region us-central1
```

## 🔍 Logging and Debugging

### Logging Configuration

```python
import logging

# Configure in app/core/logging.py
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger("app")
logger.info("Application starting")
```

### Debug Mode
When `DEBUG=True`:
- More verbose logs
- Detailed error responses
- Auto-reload on code changes
- Performance metrics

## 🚨 Error Handling

### Global Exception Handler

```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )
```

### Custom Exceptions

```python
class AppException(Exception):
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail

@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )
```

## 📚 API Documentation

### OpenAPI Configuration

```python
app = FastAPI(
    title="GenAI Misinformation Detection API",
    description="API for detecting and analyzing misinformation",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)
```

### Endpoint Documentation

```python
@router.post("/fact-check", response_model=FactCheckResponse)
async def fact_check(
    request: FactCheckRequest,
    current_user: User = Depends(get_current_user),
) -> FactCheckResponse:
    """
    Analyze content for misinformation.
    
    - **input_type**: Type of input (text, url, image)
    - **payload**: Content to analyze
    - **language**: Content language or 'auto' for auto-detection
    
    Returns a credibility analysis with citations and explanations.
    """
    # Implementation
```

## 🔄 Continuous Integration

### GitHub Actions

```yaml
name: Backend CI

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
      - name: Run tests
        run: |
          pytest
```

## 📊 Performance Monitoring

### Key Metrics to Monitor

1. **Response Time**: Average and P95 response times
2. **Request Volume**: Requests per second/minute
3. **Error Rate**: Percentage of failed requests
4. **CPU/Memory Usage**: Resource utilization
5. **External Service Latency**: Time spent calling external APIs

### Dashboard Alerts

The dashboard can be configured to alert on:
- High error rates
- Service unavailability
- Slow response times
- Resource exhaustion

## 🔄 API Versioning

The API uses URL-based versioning:

```
/api/v1/fact-check
/api/v2/fact-check
```

Version compatibility is maintained through:
- Careful deprecation
- Documentation of breaking changes
- Support for multiple versions during transition periods

## 🌐 Cross-Origin Resource Sharing (CORS)

CORS is configured in `main.py`:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Configure allowed origins in `.env`:
```
ALLOWED_ORIGINS=["http://localhost:3000","https://your-production-domain.com"]
```

## 📝 Contributing to Backend

### Development Workflow

1. **Create Feature Branch**:
   ```bash
   git checkout -b feature/new-feature
   ```

2. **Implement Changes**:
   - Follow project coding standards
   - Add tests for new functionality
   - Update documentation

3. **Run Tests Locally**:
   ```bash
   pytest
   ```

4. **Submit Pull Request**:
   - Describe changes in detail
   - Reference related issues
   - Ensure CI checks pass

### Code Style Guidelines

The project follows PEP 8 guidelines with these tools:
- **Black**: Code formatting
- **isort**: Import sorting
- **flake8**: Linting
- **mypy**: Type checking

## 🧩 Backend Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Google Cloud Python Client](https://cloud.google.com/python/docs/reference)
- [Firebase Admin Python SDK](https://firebase.google.com/docs/reference/admin/python)

---

This guide provides a comprehensive reference for backend developers working on the GenAI Misinformation Defense Platform. For setup instructions, see the [Unified Setup Guide](../docs/UNIFIED_SETUP_GUIDE.md).