# Misinformation Detection & Education Platform

A comprehensive full-stack web application for detecting misinformation and educating users through AI-powered analysis, gamified learning, and community-driven fact-checking.

## 🚀 Features

### Core Functionality
- **Multi-format Content Analysis**: Text, links, images, videos, and social media posts
- **AI-Powered Detection**: Google Vertex AI (Gemini 1.5 Flash/Pro) with grounding and embeddings
- **Multi-language Support**: Hindi, English, and 5+ Indian languages with cross-lingual retrieval
- **Fact-Checking Integration**: Fact Check Tools API, curated RSS feeds, and real-time verification
- **Media Analysis**: EXIF data extraction, image hashing, OCR, and video processing
- **Gamified Learning**: Points system, achievements, leaderboards, and educational modules
- **Community Features**: User reports, moderation tools, and collaborative fact-checking
- **Admin Dashboard**: Analytics, content moderation, and system management

### Advanced Features
- **PWA Support**: Offline functionality, push notifications, and mobile app-like experience
- **Real-time Processing**: Pub/Sub integration for scalable content analysis
- **Caching Strategy**: Firestore cache with FAISS for similarity search
- **Analytics**: Looker Studio integration for comprehensive insights
- **Security**: Privacy-first design with opt-in telemetry and ethical AI practices

## 🏗️ Architecture

### Frontend
- **Framework**: Next.js 14 with App Router
- **Styling**: Tailwind CSS with shadcn/ui components
- **PWA**: Service workers, offline support, push notifications
- **State Management**: React Query + Zustand
- **Authentication**: Firebase Auth with Google OAuth
- **UI Components**: shadcn/ui, Framer Motion, Lucide React

### Backend
- **Framework**: FastAPI with LangChain orchestration
- **Deployment**: Google Cloud Run with auto-scaling
- **Authentication**: Firebase Auth integration
- **API Documentation**: OpenAPI/Swagger with interactive docs

### AI & ML
- **Primary AI**: Google Vertex AI (Gemini 1.5 Flash/Pro)
- **Embeddings**: Vertex AI Embeddings for similarity search
- **Grounding**: Real-time fact verification with allowlist
- **Language Processing**: Cross-lingual retrieval and translation
- **Media Analysis**: OpenCV, imagehash, Tesseract OCR, FFmpeg

### Data & Storage
- **Primary Database**: Firestore (real-time, scalable)
- **Analytics**: BigQuery for large-scale data analysis
- **File Storage**: Google Cloud Storage with lifecycle policies
- **Search**: FAISS for similarity search and caching
- **Message Queue**: Pub/Sub for async processing
- **Scheduling**: Cloud Scheduler for batch operations

### Search & Fact-Checking
- **Fact Check API**: Google Fact Check Tools API
- **RSS Feeds**: Curated news sources and fact-checking sites
- **Caching**: Firestore cache with TTL
- **Similarity Search**: FAISS for finding similar claims

### DevOps & Operations
- **CI/CD**: Cloud Build with automated testing
- **Secrets**: Secret Manager for secure configuration
- **Logging**: Cloud Logging with structured logs
- **Monitoring**: Cloud Monitoring and alerting
- **Analytics**: Looker Studio dashboards

## 📊 Data Schemas

### Firestore Collections

#### `checks` Collection
```typescript
{
  id: string;
  claim: string;
  evidence: Evidence[];
  score: number; // 0-100 reliability score
  verdict: 'true' | 'false' | 'misleading' | 'unverified';
  explanations: {
    summary: string;
    reasoning: string;
    how_detected: string;
  };
  citations: Citation[];
  metadata: {
    language: string;
    content_type: 'text' | 'image' | 'video' | 'link';
    user_id: string;
    created_at: Timestamp;
    updated_at: Timestamp;
  };
  performance: {
    latency_ms: number;
    model_used: string;
    confidence: number;
  };
}
```

#### `sources` Collection
```typescript
{
  id: string;
  domain: string;
  credibility_score: number; // 0-100
  category: 'news' | 'fact_check' | 'academic' | 'government';
  notes: string;
  last_verified: Timestamp;
  allowlist_status: 'allowed' | 'blocked' | 'pending';
}
```

#### `lessons` Collection
```typescript
{
  id: string;
  technique: string;
  description: string;
  examples: string[];
  counter_habits: string[];
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  language: string;
  created_at: Timestamp;
}
```

#### `users` Collection
```typescript
{
  id: string;
  email: string;
  display_name: string;
  photo_url: string;
  points: number;
  level: number;
  achievements: Achievement[];
  preferences: {
    language: string;
    notifications: boolean;
    privacy_level: 'public' | 'private';
  };
  created_at: Timestamp;
  last_active: Timestamp;
}
```

## 🧪 Evaluation Metrics

### Accuracy
- **Precision@k**: Top-k retrieval accuracy
- **Stance Agreement**: Comparison with fact-check databases
- **False Positive Rate**: Minimize incorrect flagging

### Performance
- **Latency**: P50 < 3s, P95 < 7s
- **Throughput**: Handle concurrent requests efficiently
- **Caching Hit Rate**: Optimize for repeated queries

### User Experience
- **Helpfulness**: User ratings and feedback
- **Time-to-Citation**: Speed of source verification
- **Engagement**: Learning completion rates

### A/B Testing
- **Learn Cards**: Impact on user education
- **UI Variations**: Component performance testing
- **Feature Rollouts**: Gradual deployment strategy

## 💰 Cost Optimization Strategy

### AI Model Selection
- **Default**: Gemini 1.5 Flash (cost-effective)
- **Escalation**: Gemini 1.5 Pro for complex cases
- **Caching**: Hash-based result caching
- **Batch Processing**: Nightly index refresh

### Infrastructure
- **Firebase**: Free tier utilization
- **Cloud Run**: Min instances = 0 (scale to zero)
- **BigQuery**: Free tier (1TB/month)
- **Hackathon Credits**: Maximize usage

### Caching Strategy
- **Firestore**: TTL-based caching
- **FAISS**: Similarity search caching
- **CDN**: Static asset optimization

## 🔐 Privacy & Ethics

### Data Protection
- **No Long-term Storage**: Raw media deleted unless consent
- **Opt-in Telemetry**: User-controlled data collection
- **Anonymization**: PII removal for analytics

### AI Ethics
- **Neutral Tone**: Avoid persuasion, show sources
- **Guardrails**: Prevent hallucinations and jailbreak
- **Transparency**: Explain AI decisions clearly
- **Bias Mitigation**: Regular model evaluation

### User Control
- **Privacy Levels**: Public/private content sharing
- **Data Export**: User data portability
- **Account Deletion**: Complete data removal

## 🌍 Multilingual Support

### Language Coverage
- **MVP**: Hindi + English
- **Beta**: Bengali, Telugu, Tamil, Marathi, Kannada
- **Future**: 20+ Indian languages

### Cross-lingual Features
- **Retrieval**: Find evidence across languages
- **Answers**: Respond in input language
- **Translation**: Seamless language switching

## 🧵 LLM Processing Flow

### 1. Content Ingestion
```
Input → Language Detection → Tokenization → Content Type Classification
```

### 2. Claim Extraction
```
Gemini 1.5 Flash → Extract Claims → Identify Key Entities → Determine Stance
```

### 3. Evidence Retrieval
```
Grounding + Allowlist → Fact Check API → RSS Feeds → Similarity Search (FAISS)
```

### 4. Analysis & Scoring
```
ONNX Model → Stance Classification → Confidence Scoring → Evidence Weighting
```

### 5. Response Generation
```
Gemini Pro (if needed) → Sourced Summary → Explanations → Citations
```

### 6. Result Delivery
```
Score + Verdict + Citations + Explanations + Learning Content
```

## 🚀 Quick Start

### Prerequisites
- **Node.js 18+** and **Python 3.11+**
- **Google Cloud Platform** account with billing enabled
- **Firebase** project
- **API keys** for Vertex AI, Fact Check Tools
- **Git** for version control

### Local Development Setup

#### 1. Clone and Navigate
```bash
# Clone the repository
git clone <repository-url>
cd "GenAI Hackathon"

# Verify the project structure
ls -la
# Should show: backend/, frontend/, deployment/, docs/, etc.
```

#### 2. Backend Setup
```bash
# Navigate to backend directory
cd backend

# Create and activate virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Set up environment variables
cp env.example .env
# Edit .env with your actual API keys and configuration
```

#### 3. Frontend Setup
```bash
# Navigate to frontend directory (from project root)
cd ../frontend

# Install Node.js dependencies
npm install

# Set up environment variables
cp env.example .env.local
# Edit .env.local with your actual configuration
```

#### 4. Environment Configuration

**Backend (.env file):**
```bash
# Required: Google Cloud Configuration
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_APPLICATION_CREDENTIALS=path/to/your/credentials.json

# Required: API Keys
GEMINI_API_KEY=your-gemini-api-key
TRANSLATE_API_KEY=your-translate-api-key

# Required: Authentication
SECRET_KEY=your-secret-key-here-make-it-long-and-random

# Optional: Customize as needed
DEBUG=true
HOST=0.0.0.0
PORT=8000
```

**Frontend (.env.local file):**
```bash
# Required: API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000

# Required: Google OAuth (if using authentication)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# Optional: Analytics
NEXT_PUBLIC_GA_ID=your-google-analytics-id
```

#### 5. Running the Application

**Option A: Separate Terminals (Recommended for Development)**

```bash
# Terminal 1: Start Backend Server
cd backend
venv\Scripts\activate  # Windows
# OR source venv/bin/activate  # macOS/Linux
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Start Frontend Server
cd frontend
npm run dev
```

**Option B: Docker Compose (Production-like Environment)**

```bash
# From project root directory
docker-compose up --build

# This will start:
# - Backend on http://localhost:8000
# - Frontend on http://localhost:3000
# - Redis on localhost:6379
# - Nginx proxy on localhost:80
```

**Option C: Individual Docker Containers**

```bash
# Backend only
cd backend
docker build -t misinformation-backend .
docker run -p 8000:8000 --env-file .env misinformation-backend

# Frontend only
cd frontend
docker build -t misinformation-frontend .
docker run -p 3000:3000 --env-file .env.local misinformation-frontend
```

#### 6. Verify Installation

1. **Backend API**: Visit http://localhost:8000/docs for Swagger documentation
2. **Frontend App**: Visit http://localhost:3000 for the main application
3. **Health Check**: Backend should respond at http://localhost:8000/health

### Production Deployment

#### Google Cloud Platform Setup
```bash
# Run the automated setup script
chmod +x deployment/setup.sh
./deployment/setup.sh

# Follow the prompts to configure your GCP project
```

#### Manual Deployment
```bash
# Deploy backend to Cloud Run
cd backend
gcloud run deploy misinformation-backend \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated

# Deploy frontend to Cloud Run
cd ../frontend
gcloud run deploy misinformation-frontend \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### Development Commands

#### Backend Commands
```bash
cd backend

# Run with auto-reload (development)
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Run with production settings
uvicorn main:app --host 0.0.0.0 --port 8000

# Run tests
pytest

# Format code
black .
isort .

# Lint code
flake8 .
mypy .
```

#### Frontend Commands
```bash
cd frontend

# Development server
npm run dev

# Production build
npm run build

# Start production server
npm start

# Lint code
npm run lint

# Type checking
npm run type-check
```

### Troubleshooting

#### Common Issues

1. **Port Already in Use**
   ```bash
   # Check what's using the port
   netstat -ano | findstr :8000  # Windows
   lsof -i :8000                 # macOS/Linux
   
   # Kill the process or use different ports
   uvicorn main:app --reload --port 8001
   npm run dev -- -p 3001
   ```

2. **Python Virtual Environment Issues**
   ```bash
   # Recreate virtual environment
   deactivate
   rm -rf venv
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   pip install -r requirements.txt
   ```

3. **Node.js Dependencies Issues**
   ```bash
   # Clear npm cache and reinstall
   npm cache clean --force
   rm -rf node_modules package-lock.json
   npm install
   ```

4. **Environment Variables Not Loading**
   ```bash
   # Verify .env files exist and are in correct locations
   ls -la backend/.env
   ls -la frontend/.env.local
   
   # Check if variables are being read
   echo $GOOGLE_CLOUD_PROJECT
   ```

#### Getting Help

- **Backend Issues**: Check logs at http://localhost:8000/docs
- **Frontend Issues**: Check browser console and terminal output
- **Docker Issues**: Check container logs with `docker-compose logs`
- **GCP Issues**: Check Cloud Console logs and IAM permissions

## 📁 Project Structure

```
misinformation-detection-platform/
├── frontend/                 # Next.js PWA application
│   ├── app/                 # App Router pages
│   ├── components/          # shadcn/ui components
│   ├── lib/                 # Utilities and configurations
│   ├── hooks/               # Custom React hooks
│   └── public/              # Static assets and PWA files
├── backend/                 # FastAPI application
│   ├── app/
│   │   ├── api/            # API endpoints
│   │   ├── core/           # Configuration and middleware
│   │   ├── models/         # Data models and schemas
│   │   ├── services/       # Business logic and external APIs
│   │   └── utils/          # Utilities and helpers
│   └── tests/              # Test suite
├── deployment/             # Infrastructure and deployment
├── docs/                   # Documentation
└── shared/                 # Shared types and utilities
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🆘 Support

- Documentation: `/docs`
- Issues: GitHub Issues
- Discussions: GitHub Discussions

---

Built with ❤️ for combating misinformation and promoting digital literacy.
