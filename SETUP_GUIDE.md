# Misinformation Detection Platform - Setup Guide

This guide will walk you through setting up the complete Misinformation Detection Platform, including both local development and production deployment.

## 🚀 Quick Start

### Prerequisites

Before you begin, ensure you have the following installed:

- **Node.js 18+** and npm
- **Python 3.9+** and pip
- **Docker** and Docker Compose (for containerized deployment)
- **Google Cloud SDK** (for cloud deployment)
- **Git**

### 1. Clone the Repository

```bash
git clone <repository-url>
cd misinformation-detection-app
```

### 2. Local Development Setup

#### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp env.example .env

# Edit .env file with your configuration
# (See Environment Configuration section below)
```

#### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Copy environment file
cp env.example .env.local

# Edit .env.local file with your configuration
```

### 3. Environment Configuration

#### Backend Environment Variables

Edit `backend/.env`:

```env
# API Configuration
DEBUG=true
HOST=0.0.0.0
PORT=8000

# Google Cloud Configuration
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_APPLICATION_CREDENTIALS=path/to/credentials.json

# API Keys (Required)
GEMINI_API_KEY=your-gemini-api-key
TRANSLATE_API_KEY=your-translate-api-key

# Database Configuration
FIRESTORE_COLLECTION=misinformation_reports
BIGQUERY_DATASET=misinformation_analytics

# Storage Configuration
STORAGE_BUCKET=your-storage-bucket-name
MAX_FILE_SIZE=10485760

# Authentication
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS Configuration
ALLOWED_ORIGINS=["http://localhost:3000","http://localhost:3001"]

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60

# AI Configuration
GEMINI_MODEL=gemini-pro
GEMINI_VISION_MODEL=gemini-pro-vision

# Gamification
POINTS_PER_REPORT=10
POINTS_PER_CORRECT_DETECTION=5
POINTS_PER_LEARNING_MODULE=3
```

#### Frontend Environment Variables

Edit `frontend/.env.local`:

```env
# Next.js Configuration
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=your-nextauth-secret

# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000

# Google OAuth
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# Optional: Analytics
NEXT_PUBLIC_GA_ID=your-google-analytics-id
NEXT_PUBLIC_SENTRY_DSN=your-sentry-dsn
```

### 4. Google Cloud Setup

#### Required APIs

Enable the following Google Cloud APIs:

```bash
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable firestore.googleapis.com
gcloud services enable bigquery.googleapis.com
gcloud services enable storage.googleapis.com
gcloud services enable translate.googleapis.com
gcloud services enable identitytoolkit.googleapis.com
```

#### Service Account Setup

1. Create a service account:
```bash
gcloud iam service-accounts create misinformation-app \
    --display-name="Misinformation Detection App"
```

2. Grant necessary roles:
```bash
PROJECT_ID=$(gcloud config get-value project)
SERVICE_ACCOUNT="misinformation-app@$PROJECT_ID.iam.gserviceaccount.com"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SERVICE_ACCOUNT" \
    --role="roles/datastore.user"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SERVICE_ACCOUNT" \
    --role="roles/bigquery.dataEditor"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SERVICE_ACCOUNT" \
    --role="roles/storage.objectAdmin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SERVICE_ACCOUNT" \
    --role="roles/cloudtranslate.user"
```

3. Create and download service account key:
```bash
gcloud iam service-accounts keys create service-account-key.json \
    --iam-account=$SERVICE_ACCOUNT
```

### 5. API Keys Setup

#### Google Gemini API

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Add it to `backend/.env` as `GEMINI_API_KEY`

#### Google Cloud Translation API

1. Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
2. Enable the Translation API
3. Create credentials (API key)
4. Add it to `backend/.env` as `TRANSLATE_API_KEY`

#### Google OAuth (for authentication)

1. Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
2. Create OAuth 2.0 credentials
3. Add authorized redirect URIs:
   - `http://localhost:3000/api/auth/callback/google` (development)
   - `https://your-domain.com/api/auth/callback/google` (production)
4. Add credentials to `frontend/.env.local`

### 6. Database Setup

#### Firestore Database

```bash
# Create Firestore database
gcloud firestore databases create --region=us-central1 --type=firestore-native
```

#### BigQuery Dataset

```bash
# Create BigQuery dataset
bq mk --dataset --location=us-central1 PROJECT_ID:misinformation_analytics
```

### 7. Running the Application

#### Development Mode

```bash
# Terminal 1 - Backend
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2 - Frontend
cd frontend
npm run dev
```

#### Docker Mode

```bash
# Build and run with Docker Compose
docker-compose up --build
```

### 8. Production Deployment

#### Automated Deployment (Recommended)

Use the provided setup script:

```bash
# Make script executable
chmod +x deployment/setup.sh

# Run setup script
./deployment/setup.sh
```

#### Manual Deployment

1. Build Docker images:
```bash
# Backend
cd backend
gcloud builds submit --tag gcr.io/PROJECT_ID/misinformation-backend .

# Frontend
cd frontend
gcloud builds submit --tag gcr.io/PROJECT_ID/misinformation-frontend .
```

2. Deploy to Cloud Run:
```bash
# Deploy backend
gcloud run deploy misinformation-backend \
    --image gcr.io/PROJECT_ID/misinformation-backend \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated

# Deploy frontend
gcloud run deploy misinformation-frontend \
    --image gcr.io/PROJECT_ID/misinformation-frontend \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated
```

## 🔧 Configuration Details

### Backend Configuration

The backend uses FastAPI with the following key components:

- **Authentication**: JWT-based authentication with Google OAuth
- **Database**: Firestore for real-time data, BigQuery for analytics
- **AI Services**: Google Gemini for content analysis
- **Translation**: Google Cloud Translation API
- **Storage**: Google Cloud Storage for file uploads

### Frontend Configuration

The frontend uses Next.js 14 with:

- **Authentication**: NextAuth.js with Google provider
- **State Management**: React Query for server state
- **Styling**: Tailwind CSS with custom components
- **Forms**: React Hook Form with Zod validation
- **UI Components**: Custom component library with Lucide icons

### Database Schema

#### Firestore Collections

- `users`: User profiles and gamification data
- `reports`: User-submitted reports
- `content_analysis`: AI analysis results
- `points_transactions`: Gamification point history
- `learning_modules`: Educational content
- `quiz_submissions`: User quiz responses

#### BigQuery Tables

- `analytics_summary`: Aggregated analytics data
- `user_activity`: User interaction logs
- `content_analysis_logs`: Analysis performance metrics

## 🧪 Testing

### Backend Tests

```bash
cd backend
pytest tests/ -v
```

### Frontend Tests

```bash
cd frontend
npm test
```

### E2E Tests

```bash
npm run test:e2e
```

## 📊 Monitoring and Analytics

### Google Cloud Monitoring

- Set up monitoring for Cloud Run services
- Configure alerts for error rates and latency
- Monitor BigQuery usage and costs

### Application Metrics

- User engagement metrics
- Content analysis performance
- Gamification statistics
- Error tracking with Sentry

## 🔒 Security Considerations

### Environment Variables

- Never commit `.env` files to version control
- Use Google Secret Manager for production secrets
- Rotate API keys regularly

### Authentication

- Implement proper JWT token validation
- Use HTTPS in production
- Set up proper CORS policies

### Data Privacy

- Implement data retention policies
- Ensure GDPR compliance
- Anonymize user data for analytics

## 🚀 Performance Optimization

### Backend Optimization

- Implement caching with Redis
- Use connection pooling for databases
- Optimize AI model calls
- Implement rate limiting

### Frontend Optimization

- Use Next.js Image optimization
- Implement code splitting
- Optimize bundle size
- Use CDN for static assets

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)
- [Google Cloud Documentation](https://cloud.google.com/docs)
- [Firestore Documentation](https://firebase.google.com/docs/firestore)
- [BigQuery Documentation](https://cloud.google.com/bigquery/docs)

## 🆘 Troubleshooting

### Common Issues

1. **CORS Errors**: Check `ALLOWED_ORIGINS` in backend configuration
2. **Authentication Issues**: Verify Google OAuth credentials
3. **API Key Errors**: Ensure all required API keys are set
4. **Database Connection**: Check Firestore permissions and service account

### Getting Help

- Check the logs: `gcloud logs read`
- Review API documentation: `http://localhost:8000/api/docs`
- Open an issue on GitHub
- Contact the development team

## 🎉 Success!

Once you've completed the setup, you should have:

- ✅ A fully functional misinformation detection platform
- ✅ AI-powered content analysis
- ✅ Multi-language support
- ✅ Gamified learning system
- ✅ Admin dashboard with analytics
- ✅ Scalable cloud infrastructure

Your platform is now ready to help users detect and learn about misinformation!
