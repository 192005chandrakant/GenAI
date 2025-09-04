# FastAPI Backend Setup Guide

This guide helps you set up the Python virtual environment and run the FastAPI backend for the GenAI Misinformation Detection project.

## Prerequisites

- Python 3.11 or newer
- Windows, macOS, or Linux operating system

## Setup Steps

### 1. Create and Activate Virtual Environment

#### On Windows:
```cmd
cd C:\Users\Chandrakant\GenAI\GenAI\backend
python -m venv venv
venv\Scripts\activate.bat
```

#### On macOS/Linux:
```bash
cd /path/to/GenAI/backend
python -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies

Once the virtual environment is activated, install the required dependencies:

```bash
pip install -r minimal_requirements.txt
```

For a full installation with all features:
```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file in the backend directory:

```
# API Configuration
DEBUG=True
HOST=0.0.0.0
PORT=8000
RELOAD=True
USE_MOCKS=True

# Google Cloud Configuration (mock mode)
GOOGLE_PROJECT_ID=local-test-project

# Firebase Configuration (mock mode)
FIREBASE_PROJECT_ID=local-firebase-project
FIREBASE_PRIVATE_KEY_ID=local-key-id
FIREBASE_PRIVATE_KEY=local-private-key
FIREBASE_CLIENT_EMAIL=local-client-email
FIREBASE_CLIENT_ID=local-client-id
FIREBASE_AUTH_DOMAIN=localhost

# CORS Configuration
ALLOWED_ORIGINS=["http://localhost:3000","http://localhost:3001"]

# JWT Configuration (mock mode)
JWT_SECRET_KEY=local-testing-secret-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 4. Run the FastAPI Server

```bash
uvicorn main:app --reload
```

The server will start at `http://127.0.0.1:8000`. 

### 5. Access API Documentation

- Swagger UI: `http://127.0.0.1:8000/api/docs`
- ReDoc: `http://127.0.0.1:8000/api/redoc`

## Troubleshooting

### Import Errors

If you encounter import errors, make sure:
1. Your virtual environment is activated
2. All required packages are installed
3. You're running the server from the backend directory

### Authentication Errors

When running in mock mode:
- Firebase authentication will be mocked
- JWT tokens will work with the mock secret key

### Google API Errors

When running with `USE_MOCKS=True`:
- Google Cloud services will be mocked
- No actual API calls will be made to Google services

## Development Tips

- Use `USE_MOCKS=True` for local development without cloud dependencies
- Check the logs for detailed error information
- The server auto-reloads when code changes are detected
