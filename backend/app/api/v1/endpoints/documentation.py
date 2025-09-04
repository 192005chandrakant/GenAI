"""
Documentation endpoints for GenAI Backend API
Provides comprehensive API documentation and server information
"""

from fastapi import APIRouter, Response
from fastapi.responses import HTMLResponse
import json
from datetime import datetime
from app.core.config import settings

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
async def get_api_documentation():
    """Comprehensive API documentation and server information"""
    
    # Get all available endpoints
    endpoints = {
        "Authentication": {
            "/api/auth/login": {
                "method": "POST",
                "description": "User authentication login",
                "parameters": "email, password",
                "response": "JWT token"
            },
            "/api/auth/register": {
                "method": "POST", 
                "description": "User registration",
                "parameters": "email, password, name",
                "response": "User created confirmation"
            },
            "/api/auth/verify": {
                "method": "POST",
                "description": "Verify JWT token",
                "parameters": "Authorization header",
                "response": "Token validity"
            }
        },
        "Fact Checking": {
            "/api/v1/fact-check": {
                "method": "POST",
                "description": "Check content for misinformation",
                "parameters": "content, media_type",
                "response": "Fact check result with credibility score"
            },
            "/api/v1/fact-check/bulk": {
                "method": "POST",
                "description": "Bulk fact checking",
                "parameters": "Array of content items",
                "response": "Array of fact check results"
            }
        },
        "Content Analysis": {
            "/api/v1/analyze/text": {
                "method": "POST",
                "description": "Analyze text content",
                "parameters": "text content",
                "response": "Analysis results"
            },
            "/api/v1/analyze/media": {
                "method": "POST",
                "description": "Analyze media content",
                "parameters": "media file",
                "response": "Media analysis results"
            }
        },
        "User Management": {
            "/api/v1/users/profile": {
                "method": "GET",
                "description": "Get user profile",
                "parameters": "Authorization header",
                "response": "User profile data"
            },
            "/api/v1/users/history": {
                "method": "GET",
                "description": "Get user fact-check history",
                "parameters": "Authorization header",
                "response": "User history array"
            }
        },
        "Community": {
            "/api/v1/community/reports": {
                "method": "GET",
                "description": "Get community reports",
                "parameters": "Optional filters",
                "response": "Reports array"
            },
            "/api/v1/community/submit": {
                "method": "POST",
                "description": "Submit community report",
                "parameters": "report data",
                "response": "Submission confirmation"
            }
        },
        "Learning": {
            "/api/v1/learn/modules": {
                "method": "GET",
                "description": "Get learning modules",
                "parameters": "Optional category filter",
                "response": "Learning modules array"
            },
            "/api/v1/learn/progress": {
                "method": "GET",
                "description": "Get user learning progress",
                "parameters": "Authorization header",
                "response": "Progress data"
            }
        },
        "Dashboard & Monitoring": {
            "/api/v1/dashboard": {
                "method": "GET",
                "description": "Main dashboard interface",
                "parameters": "None",
                "response": "HTML dashboard"
            },
            "/api/v1/dashboard/status": {
                "method": "GET",
                "description": "Server status JSON",
                "parameters": "None",
                "response": "Server status data"
            },
            "/api/v1/dashboard/logs": {
                "method": "GET",
                "description": "System logs interface",
                "parameters": "None",
                "response": "HTML logs page"
            }
        }
    }
    
    # Server information
    server_info = {
        "name": "GenAI Backend API",
        "version": "1.0.0",
        "description": "Misinformation Detection Platform Backend",
        "base_url": "http://127.0.0.1:8006",
        "documentation_url": "/docs",
        "redoc_url": "/redoc",
        "openapi_url": "/openapi.json"
    }
    
    # Technology stack
    tech_stack = {
        "Backend Framework": "FastAPI",
        "Authentication": "Firebase Auth",
        "Database": "Google Firestore",
        "AI Services": "Google Vertex AI, Gemini",
        "Vector Database": "FAISS",
        "Language Support": "Google Translate API",
        "Media Processing": "Google Cloud Storage",
        "Deployment": "Docker, Google Cloud Run"
    }
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>GenAI Backend - API Documentation</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                background: #f8f9fa; 
                color: #333; 
                line-height: 1.6;
            }}
            .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
            .header {{ 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                color: white; 
                padding: 40px 20px; 
                text-align: center; 
                margin-bottom: 30px;
            }}
            .header h1 {{ font-size: 3rem; margin-bottom: 10px; }}
            .header p {{ font-size: 1.2rem; opacity: 0.9; }}
            .nav-links {{ 
                display: flex; 
                justify-content: center; 
                gap: 20px; 
                margin: 20px 0; 
                flex-wrap: wrap;
            }}
            .nav-link {{ 
                background: rgba(255,255,255,0.2); 
                color: white; 
                padding: 10px 20px; 
                border-radius: 25px; 
                text-decoration: none; 
                transition: all 0.2s;
            }}
            .nav-link:hover {{ background: rgba(255,255,255,0.3); }}
            .section {{ 
                background: white; 
                margin: 20px 0; 
                padding: 30px; 
                border-radius: 10px; 
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }}
            .section h2 {{ 
                color: #2c3e50; 
                margin-bottom: 20px; 
                font-size: 1.8rem;
                border-bottom: 3px solid #3498db;
                padding-bottom: 10px;
            }}
            .endpoints-grid {{ 
                display: grid; 
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); 
                gap: 20px; 
                margin: 20px 0;
            }}
            .endpoint-category {{ 
                background: #f8f9fa; 
                border: 1px solid #e9ecef; 
                border-radius: 8px; 
                padding: 20px;
            }}
            .endpoint-category h3 {{ 
                color: #495057; 
                margin-bottom: 15px; 
                font-size: 1.3rem;
            }}
            .endpoint {{ 
                background: white; 
                margin: 10px 0; 
                padding: 15px; 
                border-radius: 5px; 
                border-left: 4px solid #3498db;
            }}
            .endpoint-url {{ 
                font-family: 'Courier New', monospace; 
                font-weight: bold; 
                color: #2980b9; 
                font-size: 1.1rem;
            }}
            .endpoint-method {{ 
                display: inline-block; 
                background: #27ae60; 
                color: white; 
                padding: 3px 8px; 
                border-radius: 3px; 
                font-size: 0.8rem; 
                margin-right: 10px;
            }}
            .endpoint-method.POST {{ background: #e74c3c; }}
            .endpoint-method.PUT {{ background: #f39c12; }}
            .endpoint-method.DELETE {{ background: #e67e22; }}
            .info-grid {{ 
                display: grid; 
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); 
                gap: 20px;
            }}
            .info-card {{ 
                background: #ecf0f1; 
                padding: 20px; 
                border-radius: 8px; 
                border-left: 4px solid #9b59b6;
            }}
            .info-card h4 {{ color: #2c3e50; margin-bottom: 10px; }}
            .tech-item {{ 
                background: white; 
                padding: 10px; 
                margin: 5px 0; 
                border-radius: 5px; 
                display: flex; 
                justify-content: space-between;
            }}
            .back-btn {{ 
                display: inline-block; 
                background: #3498db; 
                color: white; 
                padding: 12px 25px; 
                text-decoration: none; 
                border-radius: 5px; 
                margin: 20px 0;
                transition: background 0.2s;
            }}
            .back-btn:hover {{ background: #2980b9; }}
            .code-block {{ 
                background: #2c3e50; 
                color: #ecf0f1; 
                padding: 15px; 
                border-radius: 5px; 
                font-family: 'Courier New', monospace; 
                margin: 10px 0; 
                overflow-x: auto;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>📚 GenAI Backend API</h1>
            <p>Comprehensive API Documentation & Server Information</p>
            <div class="nav-links">
                <a href="/" class="nav-link">🏠 Dashboard</a>
                <a href="/docs" class="nav-link" target="_blank">📖 OpenAPI Docs</a>
                <a href="/redoc" class="nav-link" target="_blank">📋 ReDoc</a>
                <a href="/api/v1/dashboard/status" class="nav-link" target="_blank">📊 Status API</a>
                <a href="/api/v1/dashboard/logs" class="nav-link" target="_blank">📝 Logs</a>
            </div>
        </div>
        
        <div class="container">
            <!-- Server Information -->
            <div class="section">
                <h2>🖥️ Server Information</h2>
                <div class="info-grid">
                    <div class="info-card">
                        <h4>Basic Info</h4>
                        <div class="tech-item"><span>Name:</span><span>{server_info['name']}</span></div>
                        <div class="tech-item"><span>Version:</span><span>{server_info['version']}</span></div>
                        <div class="tech-item"><span>Base URL:</span><span>{server_info['base_url']}</span></div>
                    </div>
                    <div class="info-card">
                        <h4>Documentation Links</h4>
                        <div class="tech-item"><span>OpenAPI:</span><span><a href="{server_info['documentation_url']}" target="_blank">{server_info['documentation_url']}</a></span></div>
                        <div class="tech-item"><span>ReDoc:</span><span><a href="{server_info['redoc_url']}" target="_blank">{server_info['redoc_url']}</a></span></div>
                        <div class="tech-item"><span>OpenAPI JSON:</span><span><a href="{server_info['openapi_url']}" target="_blank">{server_info['openapi_url']}</a></span></div>
                    </div>
                </div>
            </div>
            
            <!-- Technology Stack -->
            <div class="section">
                <h2>⚡ Technology Stack</h2>
                <div class="info-grid">
                    <div class="info-card">
                        <h4>Core Technologies</h4>
                        {"".join([f'<div class="tech-item"><span>{k}:</span><span>{v}</span></div>' for k, v in tech_stack.items()])}
                    </div>
                </div>
            </div>
            
            <!-- API Endpoints -->
            <div class="section">
                <h2>🔗 API Endpoints</h2>
                <div class="endpoints-grid">
    """
    
    # Add endpoint categories
    for category, endpoints_data in endpoints.items():
        html_content += f"""
                    <div class="endpoint-category">
                        <h3>{category}</h3>
        """
        for url, details in endpoints_data.items():
            html_content += f"""
                        <div class="endpoint">
                            <div class="endpoint-method {details['method']}">{details['method']}</div>
                            <div class="endpoint-url">{url}</div>
                            <p><strong>Description:</strong> {details['description']}</p>
                            <p><strong>Parameters:</strong> {details['parameters']}</p>
                            <p><strong>Response:</strong> {details['response']}</p>
                        </div>
            """
        html_content += """
                    </div>
        """
    
    html_content += f"""
                </div>
            </div>
            
            <!-- Quick Start Guide -->
            <div class="section">
                <h2>🚀 Quick Start Guide</h2>
                <h4>1. Authentication Example:</h4>
                <div class="code-block">
curl -X POST "{server_info['base_url']}/api/auth/login" \\
  -H "Content-Type: application/json" \\
  -d '{{"email": "user@example.com", "password": "password"}}'
                </div>
                
                <h4>2. Fact Check Example:</h4>
                <div class="code-block">
curl -X POST "{server_info['base_url']}/api/v1/fact-check" \\
  -H "Content-Type: application/json" \\
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \\
  -d '{{"content": "Your content to check", "media_type": "text"}}'
                </div>
                
                <h4>3. Get Server Status:</h4>
                <div class="code-block">
curl -X GET "{server_info['base_url']}/api/v1/dashboard/status"
                </div>
            </div>
            
            <!-- Response Formats -->
            <div class="section">
                <h2>📋 Response Formats</h2>
                <h4>Standard Success Response:</h4>
                <div class="code-block">
{{
  "status": "success",
  "data": {{ /* Response data */ }},
  "message": "Operation completed successfully"
}}
                </div>
                
                <h4>Standard Error Response:</h4>
                <div class="code-block">
{{
  "status": "error",
  "error": {{
    "code": "ERROR_CODE",
    "message": "Error description",
    "details": {{ /* Additional error details */ }}
  }}
}}
                </div>
            </div>
            
            <a href="/" class="back-btn">← Back to Dashboard</a>
        </div>
    </body>
    </html>
    """
    
    return html_content

@router.get("/endpoints")
async def get_endpoints_json():
    """Get all API endpoints as JSON"""
    return {
        "server_info": {
            "name": "GenAI Backend API",
            "version": "1.0.0",
            "base_url": "http://127.0.0.1:8006",
            "documentation": "/docs",
            "status": "running"
        },
        "endpoints": {
            "authentication": [
                {"path": "/api/auth/login", "method": "POST", "description": "User login"},
                {"path": "/api/auth/register", "method": "POST", "description": "User registration"},
                {"path": "/api/auth/verify", "method": "POST", "description": "Token verification"}
            ],
            "fact_checking": [
                {"path": "/api/v1/fact-check", "method": "POST", "description": "Fact check content"},
                {"path": "/api/v1/fact-check/bulk", "method": "POST", "description": "Bulk fact checking"}
            ],
            "analysis": [
                {"path": "/api/v1/analyze/text", "method": "POST", "description": "Text analysis"},
                {"path": "/api/v1/analyze/media", "method": "POST", "description": "Media analysis"}
            ],
            "monitoring": [
                {"path": "/api/v1/dashboard", "method": "GET", "description": "Dashboard interface"},
                {"path": "/api/v1/dashboard/status", "method": "GET", "description": "Server status"},
                {"path": "/api/v1/dashboard/logs", "method": "GET", "description": "System logs"}
            ]
        }
    }
