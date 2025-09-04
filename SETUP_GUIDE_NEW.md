# AI-Powered Misinformation Defense Platform - Setup Guide

This guide will walk you through setting up the complete development environment for the AI-Powered Misinformation Defense Platform.

## 📋 Prerequisites

### Required Software
- **Node.js 18.0+** - [Download](https://nodejs.org/)
- **Python 3.11+** - [Download](https://python.org/downloads/)
- **Git** - [Download](https://git-scm.com/)
- **Visual Studio Code** (recommended) - [Download](https://code.visualstudio.com/)

### Required Accounts
- **Google Cloud Platform** account with billing enabled
- **Firebase** project
- **GitHub** account (for deployment)

### Verify Prerequisites

```bash
# Check Node.js version
node --version  # Should be 18.0+

# Check Python version
python --version  # Should be 3.11+

# Check Git
git --version

# Check npm
npm --version
```

## 🚀 Quick Setup (Recommended)

### 1. Clone Repository

```bash
git clone https://github.com/your-org/misinformation-defense.git
cd misinformation-defense
```

### 2. Automated Setup

```bash
# Run the automated setup script
make setup-new-dev

# This will:
# - Set up Python virtual environment
# - Install all dependencies
# - Copy environment templates
# - Initialize configuration files
```

### 3. Configure Environment Variables

The setup script will create template files. Edit them with your actual values:

**Backend Configuration (`backend/.env`):**
```env
# === REQUIRED CONFIGURATION ===

# Google Cloud Project
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account.json

# API Keys
GEMINI_API_KEY=your-gemini-api-key
FACT_CHECK_API_KEY=your-fact-check-api-key

# Security
SECRET_KEY=your-very-long-random-secret-key-here

# === OPTIONAL CONFIGURATION ===

# Development Settings
DEBUG=true
USE_MOCKS=true  # Set to false for production
LOG_LEVEL=INFO

# Server Configuration
HOST=0.0.0.0
PORT=8000

# Database
DATABASE_URL=sqlite:///./app.db  # For development

# External Services (set USE_MOCKS=false to use real services)
TRANSLATE_API_KEY=your-translate-api-key
FIREBASE_PROJECT_ID=your-firebase-project-id
```

**Frontend Configuration (`frontend/.env.local`):**
```env
# === REQUIRED CONFIGURATION ===

# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000

# Firebase Configuration
NEXT_PUBLIC_FIREBASE_API_KEY=your-firebase-api-key
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=your-project-id

# === OPTIONAL CONFIGURATION ===

# Analytics
NEXT_PUBLIC_GA_ID=your-google-analytics-id

# Environment
NEXT_PUBLIC_ENVIRONMENT=development
```

### 4. Start Development

```bash
# Start both backend and frontend
make dev

# Check that everything is running:
# - Frontend: http://localhost:3000
# - Backend API: http://localhost:8000
# - API Docs: http://localhost:8000/api/docs
```

## 🔧 Manual Setup (Alternative)

If you prefer to set up manually or the automated script fails:

### Backend Setup

```bash
# 1. Navigate to backend directory
cd backend

# 2. Create Python virtual environment
python -m venv venv

# 3. Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 4. Upgrade pip
python -m pip install --upgrade pip

# 5. Install dependencies
pip install -r requirements.txt

# 6. Copy environment template
cp env.example .env

# 7. Edit .env file with your configuration
# Use your preferred text editor

# 8. Test the setup
python -c "import app; print('Backend setup successful!')"
```

### Frontend Setup

```bash
# 1. Navigate to frontend directory (from project root)
cd frontend

# 2. Install Node.js dependencies
npm install

# 3. Copy environment template
cp .env.example .env.local

# 4. Edit .env.local with your configuration
# Use your preferred text editor

# 5. Test the setup
npm run build
```

### Development Database Setup

```bash
# Navigate to backend directory
cd backend

# Activate virtual environment
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

# Initialize database (if using local SQLite)
python -c "
from app.core.database import init_db
init_db()
print('Database initialized successfully!')
"

# Seed with sample data (optional)
make seed
```

## 🌐 Google Cloud Platform Setup

### 1. Create GCP Project

```bash
# Install Google Cloud CLI if not already installed
# Windows: Download from https://cloud.google.com/sdk/docs/install
# macOS: brew install google-cloud-sdk
# Linux: Follow instructions at https://cloud.google.com/sdk/docs/install

# Login to Google Cloud
gcloud auth login

# Create new project
gcloud projects create your-project-id --name="Misinformation Defense"

# Set default project
gcloud config set project your-project-id

# Enable billing (required for APIs)
# Go to: https://console.cloud.google.com/billing
```

### 2. Enable Required APIs

```bash
# Enable necessary APIs
gcloud services enable \
  aiplatform.googleapis.com \
  firestore.googleapis.com \
  cloudbuild.googleapis.com \
  run.googleapis.com \
  storage.googleapis.com \
  bigquery.googleapis.com \
  translate.googleapis.com \
  factchecktools.googleapis.com
```

### 3. Create Service Account

```bash
# Create service account
gcloud iam service-accounts create misinformation-defense \
  --display-name="Misinformation Defense Service Account"

# Grant necessary roles
gcloud projects add-iam-policy-binding your-project-id \
  --member="serviceAccount:misinformation-defense@your-project-id.iam.gserviceaccount.com" \
  --role="roles/aiplatform.user"

gcloud projects add-iam-policy-binding your-project-id \
  --member="serviceAccount:misinformation-defense@your-project-id.iam.gserviceaccount.com" \
  --role="roles/datastore.user"

gcloud projects add-iam-policy-binding your-project-id \
  --member="serviceAccount:misinformation-defense@your-project-id.iam.gserviceaccount.com" \
  --role="roles/storage.admin"

# Create and download service account key
gcloud iam service-accounts keys create service-account-key.json \
  --iam-account=misinformation-defense@your-project-id.iam.gserviceaccount.com

# Move the key to a secure location
mv service-account-key.json backend/credentials/
```

### 4. Get API Keys

```bash
# Get Gemini API key
# Go to: https://aistudio.google.com/app/apikey
# Create API key and add to backend/.env

# Get Fact Check Tools API key  
# Go to: https://console.cloud.google.com/apis/credentials
# Create credentials -> API Key
# Restrict to Fact Check Tools API
```

## 🔥 Firebase Setup

### 1. Create Firebase Project

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Click "Create a project"
3. Use your existing GCP project or create new one
4. Enable Google Analytics (optional)

### 2. Setup Authentication

```bash
# Enable Authentication
# Go to: Firebase Console -> Authentication -> Get started
# Enable sign-in method: Google

# Add authorized domains for local development:
# - localhost
# - your-domain.com (for production)
```

### 3. Setup Firestore

```bash
# Create Firestore Database
# Go to: Firebase Console -> Firestore Database -> Create database
# Start in test mode (for development)
# Choose location (preferably same as GCP region)
```

### 4. Get Firebase Configuration

```bash
# Go to: Firebase Console -> Project Settings -> General
# Under "Your apps" section -> Web app -> Add app
# Copy the configuration object and add to frontend/.env.local
```

## 🧪 Verify Installation

### 1. Backend Health Check

```bash
# Start backend server
cd backend
venv\Scripts\activate  # Windows
uvicorn main:app --reload

# In another terminal, test the API
curl http://localhost:8000/health

# Expected response:
# {"status": "healthy", "timestamp": "2024-01-01T00:00:00Z"}
```

### 2. Frontend Health Check

```bash
# Start frontend server
cd frontend
npm run dev

# Visit http://localhost:3000
# You should see the application homepage
```

### 3. API Integration Test

```bash
# Test the main API endpoint
curl -X POST "http://localhost:8000/api/v1/checks" \
  -H "Content-Type: application/json" \
  -d '{
    "inputType": "text",
    "payload": "Test claim for verification",
    "language": "auto"
  }'

# Should return a JSON response with analysis results
```

### 4. Full Stack Test

1. Open http://localhost:3000 in your browser
2. Submit a test claim for analysis
3. Verify that the frontend communicates with the backend
4. Check that results are displayed correctly

## 🔄 Development Workflow

### Daily Development

```bash
# Start development environment
make dev

# Or individually:
make dev-backend    # Backend only
make dev-frontend   # Frontend only
```

### Code Quality

```bash
# Lint and format code
make lint
make format

# Run tests
make test

# Type checking
make type-check
```

### Database Operations

```bash
# Seed with sample data
make seed

# Reset database
make reset-db

# Backup database
make backup-db
```

## 🚨 Troubleshooting

### Common Issues

#### 1. Port Already in Use

```bash
# Check what's using the port
netstat -ano | findstr :8000  # Windows
lsof -i :8000                 # macOS/Linux

# Use different ports
make dev-backend PORT=8001
npm run dev -- -p 3001
```

#### 2. Python Dependencies

```bash
# Clear pip cache
pip cache purge

# Recreate virtual environment
deactivate
rmdir /s venv  # Windows
rm -rf venv    # macOS/Linux
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

#### 3. Node.js Dependencies

```bash
# Clear npm cache
npm cache clean --force

# Delete node_modules and reinstall
rmdir /s node_modules  # Windows
rm -rf node_modules    # macOS/Linux
del package-lock.json  # Windows
rm package-lock.json   # macOS/Linux
npm install
```

#### 4. Environment Variables

```bash
# Check if .env files exist
dir backend\.env frontend\.env.local  # Windows
ls -la backend/.env frontend/.env.local  # macOS/Linux

# Verify variables are loaded
echo %GOOGLE_CLOUD_PROJECT%  # Windows
echo $GOOGLE_CLOUD_PROJECT   # macOS/Linux
```

#### 5. Google Cloud Authentication

```bash
# Re-authenticate
gcloud auth login
gcloud auth application-default login

# Check current project
gcloud config get-value project

# Set project if needed
gcloud config set project your-project-id
```

#### 6. Firebase Issues

```bash
# Install Firebase CLI
npm install -g firebase-tools

# Login to Firebase
firebase login

# List projects
firebase projects:list

# Set project
firebase use your-project-id
```

### Getting Help

#### 1. Check Logs

```bash
# Backend logs (in development)
# Check terminal where uvicorn is running

# Frontend logs
# Check browser console (F12)

# Production logs
gcloud logs read --project=your-project-id
```

#### 2. Debug Mode

```bash
# Enable debug mode
# In backend/.env:
DEBUG=true
LOG_LEVEL=DEBUG

# In frontend/.env.local:
NEXT_PUBLIC_DEBUG=true
```

#### 3. Health Checks

```bash
# Backend health
curl http://localhost:8000/health

# API documentation
# Visit: http://localhost:8000/api/docs

# Frontend health
# Visit: http://localhost:3000
```

## 🎯 Next Steps

After successful setup:

1. **Explore the API**: Visit http://localhost:8000/api/docs
2. **Test functionality**: Submit test claims through the frontend
3. **Review configuration**: Check all environment variables
4. **Read documentation**: Explore the docs/ folder
5. **Start development**: Begin implementing new features

## 📚 Additional Resources

### Documentation
- [Roadmap](roadmap.md) - Feature roadmap and implementation plan
- [API Documentation](http://localhost:8000/api/docs) - Interactive API docs
- [Contributing Guide](CONTRIBUTING.md) - How to contribute

### External Resources
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)
- [Google Cloud Documentation](https://cloud.google.com/docs)
- [Firebase Documentation](https://firebase.google.com/docs)

### Support
- [GitHub Issues](https://github.com/your-org/misinformation-defense/issues)
- [GitHub Discussions](https://github.com/your-org/misinformation-defense/discussions)

---

**Setup complete! 🎉 You're ready to start developing the AI-Powered Misinformation Defense Platform.**
