# GenAI Backend Server Documentation

## 🚀 Overview

The GenAI Backend is a comprehensive misinformation detection platform built with FastAPI, featuring real-time monitoring, detailed analytics, and extensive API documentation.

## 📊 Dashboard Features

### Main Dashboard
- **URL**: `http://127.0.0.1:8006/`
- **Features**: 
  - Real-time server monitoring
  - Service health status
  - System resource usage
  - Performance metrics
  - Server statistics with uptime tracking
  - Auto-refresh every 30 seconds

### Server Statistics Tracking
- **Total Requests**: Complete request counter
- **Success Rate**: Request success percentage
- **Uptime Tracking**: Detailed server uptime (days, hours, minutes, seconds)
- **Performance Metrics**: Peak CPU/memory usage, data processed
- **Request Rate**: Requests per second/minute/hour
- **Service Health**: Real-time monitoring of all backend services

## 📚 Documentation Endpoints

### 1. API Documentation Portal
- **URL**: `http://127.0.0.1:8006/api/v1/docs-api/`
- **Description**: Comprehensive API guide with examples
- **Features**:
  - Complete endpoint listing by category
  - Request/response examples
  - Quick start guide
  - Technology stack information
  - Interactive documentation

### 2. OpenAPI Documentation
- **URL**: `http://127.0.0.1:8006/docs`
- **Description**: Interactive Swagger UI documentation
- **Features**:
  - Try-it-out functionality
  - Request/response schemas
  - Authentication testing

### 3. ReDoc Documentation
- **URL**: `http://127.0.0.1:8006/redoc`
- **Description**: Alternative API documentation format
- **Features**:
  - Clean, readable format
  - Detailed parameter descriptions
  - Response examples

## 🔗 API Endpoints

### Core Endpoints

#### Authentication
- `POST /api/auth/login` - User authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/verify` - Token verification

#### Fact Checking
- `POST /api/v1/fact-check` - Single content fact check
- `POST /api/v1/fact-check/bulk` - Bulk fact checking

#### Content Analysis
- `POST /api/v1/analyze/text` - Text content analysis
- `POST /api/v1/analyze/media` - Media content analysis

#### User Management
- `GET /api/v1/users/profile` - User profile
- `GET /api/v1/users/history` - User fact-check history

#### Community Features
- `GET /api/v1/community/reports` - Community reports
- `POST /api/v1/community/submit` - Submit community report

#### Learning Platform
- `GET /api/v1/learn/modules` - Learning modules
- `GET /api/v1/learn/progress` - User progress

### Monitoring Endpoints

#### Dashboard & Status
- `GET /api/v1/dashboard/` - Main dashboard interface
- `GET /api/v1/dashboard/status` - Server status JSON
- `GET /api/v1/dashboard/logs` - System logs interface

#### Documentation
- `GET /api/v1/docs-api/` - API documentation portal
- `GET /api/v1/docs-api/endpoints` - Endpoints list JSON

## 📈 Server Statistics

### Real-time Metrics
- **Uptime**: Server running time with detailed breakdown
- **Request Statistics**: Total, successful, failed requests
- **Performance Tracking**: CPU, memory, disk usage
- **Network Statistics**: Data sent/received
- **Process Information**: Memory usage, thread count
- **Service Health**: Status of all backend services

### Performance Data
- **Peak Usage Tracking**: Maximum CPU and memory usage
- **Request Rate**: Requests per second/minute/hour
- **Success Rate**: Percentage of successful requests
- **Data Processing**: Total data processed in MB
- **User Metrics**: Number of users served

## 🛠️ Technology Stack

### Backend Framework
- **FastAPI**: High-performance web framework
- **Python 3.11+**: Programming language
- **Uvicorn**: ASGI server

### AI & Machine Learning
- **Google Vertex AI**: Advanced AI capabilities
- **Google Gemini**: Large language model
- **FAISS**: Vector similarity search
- **Google Translate API**: Multi-language support

### Database & Storage
- **Google Firestore**: NoSQL database
- **Google Cloud Storage**: Media file storage

### Authentication & Security
- **Firebase Auth**: User authentication
- **JWT Tokens**: Secure API access

### Monitoring & Analytics
- **psutil**: System resource monitoring
- **Real-time Dashboard**: Server status tracking
- **Comprehensive Logging**: Activity tracking

## 🚀 Quick Start

### 1. Start the Server
```bash
# Using the batch file
start_dashboard.bat

# Or manually
python main.py
```

### 2. Access the Dashboard
Open your browser to: `http://127.0.0.1:8006`

### 3. Explore the API
- Dashboard: `http://127.0.0.1:8006/`
- API Guide: `http://127.0.0.1:8006/api/v1/docs-api/`
- OpenAPI Docs: `http://127.0.0.1:8006/docs`

### 4. Test the API
```bash
# Get server status
curl http://127.0.0.1:8006/api/v1/dashboard/status

# Check endpoints
curl http://127.0.0.1:8006/api/v1/docs-api/endpoints
```

## 📊 Monitoring Features

### System Monitoring
- **CPU Usage**: Real-time CPU utilization
- **Memory Usage**: RAM consumption and availability
- **Disk Usage**: Storage utilization
- **Network Activity**: Data transfer statistics
- **Process Metrics**: Application-specific resource usage

### Service Health Monitoring
- **Vertex AI Service**: AI model connectivity
- **Gemini Service**: Language model status
- **Firestore Service**: Database connectivity
- **FAISS Service**: Vector search availability
- **Translation Service**: Multi-language support
- **Fact Check Service**: Core functionality

### Performance Analytics
- **Request Tracking**: Complete request lifecycle
- **Response Times**: API performance metrics
- **Error Rates**: System reliability metrics
- **Peak Usage**: Resource utilization patterns
- **User Activity**: Service usage statistics

## 🔧 Configuration

### Environment Variables
- `USE_MOCKS`: Enable mock services for development
- `PROJECT_NAME`: Application name
- `VERSION`: Application version
- `ENVIRONMENT`: Deployment environment

### Mock Services
When Google Cloud credentials are not available, the system automatically falls back to mock services for development purposes.

## 🎯 Key Features

1. **Comprehensive Monitoring**: Real-time server and service monitoring
2. **Detailed Documentation**: Multiple documentation formats with examples
3. **Performance Tracking**: Complete statistics and analytics
4. **Service Health**: Continuous monitoring of all backend components
5. **User-friendly Interface**: Clean, modern dashboard design
6. **Auto-refresh**: Real-time updates without manual refresh
7. **Quick Actions**: Easy access to documentation and tools
8. **Mobile Responsive**: Dashboard works on all device sizes

## 📞 Support & Development

- **Dashboard**: Full server monitoring and control
- **Documentation**: Comprehensive API guides and examples
- **Statistics**: Detailed performance and usage analytics
- **Health Monitoring**: Real-time service status tracking
- **Easy Deployment**: One-click server startup

The GenAI Backend provides enterprise-grade monitoring, documentation, and analytics for a complete misinformation detection platform.
