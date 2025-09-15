# AI-Powered Misinformation Defense Platform - Complete Setup Guide

This comprehensive guide walks you through setting up the complete AI-Powered Misinformation Defense Platform for development, testing, and deployment.

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

#### Method 1: Quick Setup with Development Templates

For rapid development setup, use the pre-configured development templates:

```bash
# Backend setup
cd backend
cp .env.development .env
# Edit backend/.env with your actual credentials

# Frontend setup
cd ../frontend
cp .env.development .env.local
# Edit frontend/.env.local with your actual credentials
```

#### Method 2: Manual Configuration from Examples

For custom setup, use the example templates:

```bash
# Backend configuration
cd backend
cp .env.example .env
# Edit backend/.env with your configuration

# Frontend configuration
cd ../frontend
cp .env.example .env.local
# Edit frontend/.env.local with your configuration
```

#### Backend Configuration (`backend/.env`)

**Key configurations to update:**
```env
# === REQUIRED FOR PRODUCTION ===

# Google Cloud Project (replace with your project)
GOOGLE_PROJECT_ID=your-gcp-project-id
GOOGLE_APPLICATION_CREDENTIALS=./secrets/service-account-key.json

# Firebase Configuration (replace with your project)
FIREBASE_PROJECT_ID=your-firebase-project-id
FIREBASE_PRIVATE_KEY_ID=your-firebase-private-key-id
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nyour-firebase-private-key\n-----END PRIVATE KEY-----"
FIREBASE_CLIENT_EMAIL=firebase-adminsdk-xxxxx@your-project.iam.gserviceaccount.com

# API Keys (replace with your keys)
GEMINI_API_KEY=your-gemini-api-key
TRANSLATE_API_KEY=your-google-translate-api-key
FACT_CHECK_API_KEY=your-fact-check-tools-api-key

# Security (generate secure values)
JWT_SECRET_KEY=your-super-secret-jwt-key-min-32-characters

# OAuth (replace with your credentials)
GITHUB_CLIENT_ID=your-github-oauth-client-id
GITHUB_CLIENT_SECRET=your-github-oauth-client-secret

# File Storage (replace with your credentials)
CLOUDINARY_CLOUD_NAME=your-cloudinary-cloud-name
CLOUDINARY_API_KEY=your-cloudinary-api-key
CLOUDINARY_API_SECRET=your-cloudinary-api-secret

# === DEVELOPMENT SETTINGS ===
DEBUG=true
USE_MOCKS=true  # Set to false for production
```
#### Frontend Configuration (`frontend/.env.local`)

**Key configurations to update:**
```env
# === REQUIRED FOR PRODUCTION ===

# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000

# Firebase Configuration (must match backend project)
NEXT_PUBLIC_FIREBASE_API_KEY=your-firebase-api-key
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=your-firebase-project-id
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=your-project.firebasestorage.app
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=your-messaging-sender-id
NEXT_PUBLIC_FIREBASE_APP_ID=your-firebase-app-id

# NextAuth Configuration
NEXTAUTH_URL=http://localhost:3001
NEXTAUTH_SECRET=your-nextauth-secret-key-min-32-characters

# OAuth Configuration (replace with your credentials)
GOOGLE_CLIENT_ID=your-google-oauth-client-id
GOOGLE_CLIENT_SECRET=your-google-oauth-client-secret
GITHUB_CLIENT_ID=your-github-oauth-client-id
GITHUB_CLIENT_SECRET=your-github-oauth-client-secret

# === DEVELOPMENT SETTINGS ===
NEXT_PUBLIC_DEBUG=false
NEXT_PUBLIC_ENVIRONMENT=development
```

> **🔒 Security Note**: 
> - The `.env.development` files contain placeholder credentials for easy setup
> - Replace all placeholder values with your actual credentials before deploying
> - Never commit files containing real credentials to version control
> - Use `.env.local` for frontend and `.env` for backend in local development

## 🖥️ Backend Setup

### 1. Set Up Python Virtual Environment

```bash
# Navigate to backend directory
cd backend

# Create Python virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate.bat
# macOS/Linux:
source venv/bin/activate

# Upgrade pip
python -m pip install --upgrade pip
```

### 2. Install Backend Dependencies

For a minimal installation with basic functionality:
```bash
pip install -r minimal_requirements.txt
```

For a full installation with all features:
```bash
pip install -r requirements.txt
```

### 3. Run the FastAPI Backend Server

```bash
# Make sure your virtual environment is activated
uvicorn main:app --reload
```

The server will start at `http://127.0.0.1:8000`.

### 4. Access Backend Documentation

- Swagger UI: `http://127.0.0.1:8000/api/docs`
- ReDoc: `http://127.0.0.1:8000/api/redoc`
- API Documentation Portal: `http://127.0.0.1:8000/api/v1/docs-api/` (if enabled)

### 5. Backend Dashboard (if enabled)

Access the backend monitoring dashboard at:
```
http://127.0.0.1:8006/
```

## 🎨 Frontend Setup

### 1. Install Node.js Dependencies

```bash
# Navigate to frontend directory (from project root)
cd frontend

# Install Node.js dependencies
npm install
```

### 2. Configure Firebase

See the [Firebase Configuration Guide](../frontend/FIREBASE_SETUP_GUIDE.md) for detailed instructions on setting up Firebase for authentication and other services.

### 3. Start the Next.js Development Server

```bash
# From the frontend directory
npm run dev
```

This will start the frontend development server at `http://localhost:3000` (or `http://localhost:3001` depending on your configuration).

## 🌐 Google Cloud Platform Setup

### 1. Create GCP Project

```bash
# Install Google Cloud CLI if not already installed
# Windows: Download from https://cloud.google.com/sdk/docs/install

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
gcloud iam service-accounts keys create backend/secrets/service-account-key.json \
  --iam-account=misinformation-defense@your-project-id.iam.gserviceaccount.com
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
# Enable sign-in methods: Email/Password and Google
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
# Under "Your apps" section -> Web app -> Add app (if not already added)
# Copy the configuration object and add to frontend/.env.local
```

For detailed Firebase setup, see the [Firebase Configuration Guide](../frontend/FIREBASE_SETUP_GUIDE.md).

## 🔐 OAuth Configuration

### Google OAuth Setup

For detailed instructions on setting up Google OAuth, see the [Google OAuth Setup Guide](../frontend/docs/GOOGLE_OAUTH_SETUP.md).

### GitHub OAuth Setup

For detailed instructions on setting up GitHub OAuth, see the [GitHub OAuth Setup Guide](../docs/GITHUB_OAUTH_SETUP.md).

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

## 🔄 Development Workflow

### Start Development Environment

```bash
# Start both backend and frontend
make dev

# Or individually:
make dev-backend    # Backend only
make dev-frontend   # Frontend only

# For development with mock services (no real API calls)
make dev-with-mocks
```

### Using Mock Services

For development without cloud dependencies:

1. Set `USE_MOCKS=True` in `backend/.env`
2. This will:
   - Mock Google Cloud services
   - Mock Firebase authentication
   - Use JWT tokens with the mock secret key
   - Simulate API responses

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
rmdir /s /q venv  # Windows
rm -rf venv       # macOS/Linux
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

#### 3. Node.js Dependencies

```bash
# Clear npm cache
npm cache clean --force

# Delete node_modules and reinstall
rmdir /s /q node_modules  # Windows
rm -rf node_modules       # macOS/Linux
del package-lock.json     # Windows
rm package-lock.json      # macOS/Linux
npm install
```

#### 4. Firebase Authentication Errors

If you encounter the error `Firebase: Error (auth/api-key-not-valid)`:

1. Follow the detailed instructions in the [Firebase Configuration Guide](../frontend/FIREBASE_SETUP_GUIDE.md)
2. Ensure your API keys in `.env.local` match your Firebase project
3. Verify that authentication methods are enabled in Firebase console

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

## 🚀 Deployment

### Development Deployment

```bash
# Using Cloud Run and Firebase
make deploy-dev
```

### Production Deployment

```bash
# Interactive confirmation required
make deploy-prod
```

For detailed deployment instructions, see the [Deployment Guide](../deployment/README.md).

## 📚 Additional Resources

- [Main README](../README.md) - Project overview and features
- [Backend Documentation](../backend/BACKEND_DOCUMENTATION.md) - Backend API and features
- [Roadmap](../roadmap.md) - Feature roadmap and implementation plan
- [Contributing Guide](../CONTRIBUTING.md) - How to contribute

---

**Setup complete! 🎉 You're ready to start developing the AI-Powered Misinformation Defense Platform.**