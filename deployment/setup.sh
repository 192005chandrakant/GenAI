#!/bin/bash

# Misinformation Detection Platform - Google Cloud Setup Script
# This script sets up the entire infrastructure on Google Cloud Platform

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ID=""
REGION="us-central1"
ZONE="us-central1-a"

echo -e "${BLUE}🚀 Misinformation Detection Platform - Google Cloud Setup${NC}"
echo "=================================================="

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}❌ Google Cloud SDK is not installed. Please install it first.${NC}"
    echo "Visit: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Get project ID
if [ -z "$PROJECT_ID" ]; then
    echo -e "${YELLOW}Enter your Google Cloud Project ID:${NC}"
    read -r PROJECT_ID
fi

# Set project
echo -e "${BLUE}Setting project to: $PROJECT_ID${NC}"
gcloud config set project "$PROJECT_ID"

# Enable required APIs
echo -e "${BLUE}Enabling required APIs...${NC}"
APIS=(
    "cloudbuild.googleapis.com"
    "run.googleapis.com"
    "firestore.googleapis.com"
    "bigquery.googleapis.com"
    "storage.googleapis.com"
    "translate.googleapis.com"
    "identitytoolkit.googleapis.com"
    "cloudresourcemanager.googleapis.com"
    "iam.googleapis.com"
)

for api in "${APIS[@]}"; do
    echo -e "${YELLOW}Enabling $api...${NC}"
    gcloud services enable "$api" --quiet
done

# Create Firestore database
echo -e "${BLUE}Setting up Firestore database...${NC}"
gcloud firestore databases create --region="$REGION" --type=firestore-native --quiet || echo "Firestore database already exists"

# Create BigQuery dataset
echo -e "${BLUE}Setting up BigQuery dataset...${NC}"
bq mk --dataset --location="$REGION" "$PROJECT_ID:misinformation_analytics" || echo "BigQuery dataset already exists"

# Create Cloud Storage bucket
echo -e "${BLUE}Setting up Cloud Storage bucket...${NC}"
BUCKET_NAME="misinformation-uploads-$PROJECT_ID"
gsutil mb -l "$REGION" "gs://$BUCKET_NAME" || echo "Storage bucket already exists"

# Set bucket permissions
gsutil iam ch allUsers:objectViewer "gs://$BUCKET_NAME"

# Create service account for the application
echo -e "${BLUE}Creating service account...${NC}"
SERVICE_ACCOUNT_NAME="misinformation-app"
SERVICE_ACCOUNT_EMAIL="$SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com"

gcloud iam service-accounts create "$SERVICE_ACCOUNT_NAME" \
    --display-name="Misinformation Detection App" \
    --description="Service account for Misinformation Detection Platform" || echo "Service account already exists"

# Grant necessary roles
echo -e "${BLUE}Granting necessary roles...${NC}"
ROLES=(
    "roles/datastore.user"
    "roles/bigquery.dataEditor"
    "roles/bigquery.jobUser"
    "roles/storage.objectAdmin"
    "roles/cloudtranslate.user"
    "roles/run.admin"
    "roles/iam.serviceAccountUser"
)

for role in "${ROLES[@]}"; do
    echo -e "${YELLOW}Granting $role...${NC}"
    gcloud projects add-iam-policy-binding "$PROJECT_ID" \
        --member="serviceAccount:$SERVICE_ACCOUNT_EMAIL" \
        --role="$role" --quiet
done

# Create and download service account key
echo -e "${BLUE}Creating service account key...${NC}"
KEY_FILE="service-account-key.json"
gcloud iam service-accounts keys create "$KEY_FILE" \
    --iam-account="$SERVICE_ACCOUNT_EMAIL" || echo "Key file already exists"

# Build and push Docker images
echo -e "${BLUE}Building and pushing Docker images...${NC}"

# Build backend image
echo -e "${YELLOW}Building backend image...${NC}"
cd backend
gcloud builds submit --tag "gcr.io/$PROJECT_ID/misinformation-backend" . --quiet

# Build frontend image
echo -e "${YELLOW}Building frontend image...${NC}"
cd ../frontend
gcloud builds submit --tag "gcr.io/$PROJECT_ID/misinformation-frontend" . --quiet

cd ..

# Deploy to Cloud Run
echo -e "${BLUE}Deploying to Cloud Run...${NC}"

# Deploy backend
echo -e "${YELLOW}Deploying backend...${NC}"
gcloud run deploy misinformation-backend \
    --image "gcr.io/$PROJECT_ID/misinformation-backend" \
    --platform managed \
    --region "$REGION" \
    --allow-unauthenticated \
    --set-env-vars "GOOGLE_CLOUD_PROJECT=$PROJECT_ID,STORAGE_BUCKET=$BUCKET_NAME" \
    --service-account "$SERVICE_ACCOUNT_EMAIL" \
    --memory 4Gi \
    --cpu 2 \
    --max-instances 10 \
    --quiet

# Get backend URL
BACKEND_URL=$(gcloud run services describe misinformation-backend --region="$REGION" --format="value(status.url)")

# Deploy frontend
echo -e "${YELLOW}Deploying frontend...${NC}"
gcloud run deploy misinformation-frontend \
    --image "gcr.io/$PROJECT_ID/misinformation-frontend" \
    --platform managed \
    --region "$REGION" \
    --allow-unauthenticated \
    --set-env-vars "NEXT_PUBLIC_API_URL=$BACKEND_URL" \
    --memory 2Gi \
    --cpu 1 \
    --max-instances 10 \
    --quiet

# Get frontend URL
FRONTEND_URL=$(gcloud run services describe misinformation-frontend --region="$REGION" --format="value(status.url)")

# Create environment files
echo -e "${BLUE}Creating environment files...${NC}"

# Backend .env
cat > backend/.env << EOF
# API Configuration
DEBUG=false
HOST=0.0.0.0
PORT=8000

# Google Cloud Configuration
GOOGLE_CLOUD_PROJECT=$PROJECT_ID
GOOGLE_APPLICATION_CREDENTIALS=./service-account-key.json

# API Keys (You need to add these manually)
GEMINI_API_KEY=your-gemini-api-key
TRANSLATE_API_KEY=your-translate-api-key

# Database Configuration
FIRESTORE_COLLECTION=misinformation_reports
BIGQUERY_DATASET=misinformation_analytics

# Storage Configuration
STORAGE_BUCKET=$BUCKET_NAME
MAX_FILE_SIZE=10485760

# Authentication
SECRET_KEY=$(openssl rand -hex 32)
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS Configuration
ALLOWED_ORIGINS=["$FRONTEND_URL","http://localhost:3000"]

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60

# AI Configuration
GEMINI_MODEL=gemini-pro
GEMINI_VISION_MODEL=gemini-pro-vision

# Gamification
POINTS_PER_REPORT=10
POINTS_PER_CORRECT_DETECTION=5
POINTS_PER_LEARNING_MODULE=3
EOF

# Frontend .env.local
cat > frontend/.env.local << EOF
# Next.js Configuration
NEXTAUTH_URL=$FRONTEND_URL
NEXTAUTH_SECRET=$(openssl rand -hex 32)

# API Configuration
NEXT_PUBLIC_API_URL=$BACKEND_URL

# Google OAuth (You need to add these manually)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
EOF

# Clean up service account key
rm -f "$KEY_FILE"

echo -e "${GREEN}✅ Setup completed successfully!${NC}"
echo "=================================================="
echo -e "${BLUE}Frontend URL:${NC} $FRONTEND_URL"
echo -e "${BLUE}Backend URL:${NC} $BACKEND_URL"
echo -e "${BLUE}API Documentation:${NC} $BACKEND_URL/api/docs"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Add your Gemini API key to backend/.env"
echo "2. Add your Google OAuth credentials to frontend/.env.local"
echo "3. Redeploy the services with the updated environment variables"
echo ""
echo -e "${YELLOW}To redeploy with updated environment:${NC}"
echo "gcloud run services replace deployment/cloud-run.yaml"
echo ""
echo -e "${GREEN}🎉 Your Misinformation Detection Platform is now live!${NC}"
