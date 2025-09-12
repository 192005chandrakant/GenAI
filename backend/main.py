"""
Main FastAPI application for the Misinformation Detection API.
"""
import logging
import socket
import os
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse, Response
from contextlib import asynccontextmanager

from app.core.config import settings
from app.api.v1.api import api_router
from app.services.firestore_service import firestore_service

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Global server info
SERVER_INFO = {
    "start_time": None,
    "host": None,
    "port": None,
    "urls": {},
    "environment": "development" if settings.USE_MOCKS else "production"
}

def get_server_urls(host: str, port: int) -> dict:
    """Generate server URLs dynamically."""
    # Determine the actual host
    if host == "0.0.0.0":
        hostname = socket.gethostname()
        try:
            local_ip = socket.gethostbyname(hostname)
        except:
            local_ip = "127.0.0.1"
        hosts = ["localhost", "127.0.0.1", local_ip, hostname]
    else:
        hosts = [host]
    
    urls = {}
    for h in hosts:
        base_url = f"http://{h}:{port}"
        urls[h] = {
            "base": base_url,
            "dashboard": f"{base_url}/api/v1/dashboard",
            "docs": f"{base_url}/api/docs",
            "redoc": f"{base_url}/api/redoc",
            "status": f"{base_url}/api/v1/dashboard/status",
            "health": f"{base_url}/health"
        }
    
    return urls


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    start_time = datetime.utcnow()
    SERVER_INFO["start_time"] = start_time
    SERVER_INFO["host"] = settings.host
    SERVER_INFO["port"] = settings.port
    SERVER_INFO["urls"] = get_server_urls(settings.host, settings.port)
    
    try:
        # Test database connection
        await firestore_service.get_analytics_summary()
    except Exception as e:
        logger.warning("Database connection not available in mock mode")
    
    # Print server startup information
    logger.info("=" * 60)
    logger.info("🚀 GenAI Backend Server is running!")
    logger.info("=" * 60)
    logger.info("Environment: %s", SERVER_INFO["environment"])
    logger.info("Available URLs:")
    
    # Get local URLs for easy access
    local_urls = SERVER_INFO["urls"].get("localhost", {})
    if local_urls:
        logger.info("📚 API Documentation: %s", local_urls["docs"])
        logger.info("📖 ReDoc Documentation: %s", local_urls["redoc"])
        logger.info("🎯 Main API: %s", local_urls["base"])
        logger.info("📊 Dashboard: %s", local_urls["dashboard"])
        logger.info("💓 Health Check: %s", local_urls["health"])
    
    logger.info("=" * 60)
    logger.info("Press CTRL+C to stop the server")
    logger.info("=" * 60)
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down GenAI Backend Server...")


# Create FastAPI app - serve docs at both /docs and /api/docs 
app = FastAPI(
    title=settings.project_name,
    version=settings.version,
    description="AI-powered misinformation detection and education platform",
    # Provide docs at multiple paths to avoid redirects
    docs_url=None,  # We'll manually define the docs routes
    redoc_url=None, # We'll manually define the redoc routes
    openapi_url="/api/openapi.json",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix=settings.api_v1_str)


@app.get("/")
async def root():
    """Root endpoint - return API info directly instead of redirecting."""
    uptime = datetime.utcnow() - SERVER_INFO["start_time"] if SERVER_INFO["start_time"] else None
    
    return {
        "message": "Welcome to GenAI Misinformation Detection API",
        "version": settings.version,
        "status": "running",
        "uptime": str(uptime) if uptime else None,
        "endpoints": {
            "dashboard": "/api/v1/dashboard",
            "api_docs": "/api/docs",
            "health": "/health"
        }
    }


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    """Serve Swagger UI at /docs."""
    from fastapi.openapi.docs import get_swagger_ui_html
    
    return get_swagger_ui_html(
        openapi_url="/api/openapi.json",
        title=f"{app.title} - Swagger UI",
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css",
    )

@app.get("/api/docs", include_in_schema=False)
async def custom_api_swagger_ui_html():
    """Serve Swagger UI at /api/docs."""
    from fastapi.openapi.docs import get_swagger_ui_html
    
    return get_swagger_ui_html(
        openapi_url="/api/openapi.json",
        title=f"{app.title} - API Documentation",
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css",
    )

@app.get("/redoc", include_in_schema=False)
async def custom_redoc_html():
    """Serve ReDoc at /redoc."""
    from fastapi.openapi.docs import get_redoc_html
    
    return get_redoc_html(
        openapi_url="/api/openapi.json",
        title=f"{app.title} - ReDoc",
        redoc_js_url="https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js",
    )

@app.get("/api/redoc", include_in_schema=False)
async def custom_api_redoc_html():
    """Serve ReDoc at /api/redoc."""
    from fastapi.openapi.docs import get_redoc_html
    
    return get_redoc_html(
        openapi_url="/api/openapi.json",
        title=f"{app.title} - API Reference",
        redoc_js_url="https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js",
    )


@app.get("/api")
async def api_info():
    """Dynamic API information endpoint."""
    return {
        "message": "Welcome to GenAI Misinformation Detection API",
        "version": settings.version,
        "environment": SERVER_INFO["environment"],
        "server": {
            "host": SERVER_INFO["host"],
            "port": SERVER_INFO["port"],
            "start_time": SERVER_INFO["start_time"].isoformat() if SERVER_INFO["start_time"] else None,
            "uptime_seconds": int((datetime.utcnow() - SERVER_INFO["start_time"]).total_seconds()) if SERVER_INFO["start_time"] else 0
        },
        "urls": SERVER_INFO["urls"],
        "endpoints": {
            "dashboard": "/api/v1/dashboard",
            "api_docs": "/api/docs",
            "docs": "/docs", 
            "redoc": "/redoc",
            "api_redoc": "/api/redoc",
            "status": "/api/v1/dashboard/status",
            "health": "/health"
        }
    }


@app.get("/server-info")
async def server_info():
    """Live server information endpoint."""
    uptime = datetime.utcnow() - SERVER_INFO["start_time"] if SERVER_INFO["start_time"] else None
    
    return {
        "server": {
            "name": "GenAI Backend Server", 
            "version": settings.version,
            "environment": SERVER_INFO["environment"],
            "host": SERVER_INFO["host"],
            "port": SERVER_INFO["port"],
            "start_time": SERVER_INFO["start_time"].isoformat() if SERVER_INFO["start_time"] else None,
            "uptime": str(uptime) if uptime else None,
            "uptime_seconds": int(uptime.total_seconds()) if uptime else 0,
            "status": "running"
        },
        "urls": SERVER_INFO["urls"],
        "features": [
            "AI-powered fact checking",
            "Multi-language support", 
            "Real-time analysis",
            "Educational content",
            "Community reporting",
            "Comprehensive dashboard",
            "Live monitoring"
        ]
    }


@app.get("/favicon.ico")
async def favicon():
    """Serve favicon to prevent 404 errors."""
    from fastapi.responses import FileResponse
    import os
    
    # Check if favicon exists in a few possible locations
    favicon_paths = [
        os.path.join("public", "favicon.ico"),
        os.path.join("static", "favicon.ico"),
        os.path.join("app", "static", "favicon.ico")
    ]
    
    for path in favicon_paths:
        if os.path.isfile(path):
            return FileResponse(path)
    
    # If favicon not found, return an empty response to prevent 404
    return Response(content=b"", media_type="image/x-icon")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        # Test database connection
        await firestore_service.get_analytics_summary()
        return {
            "status": "healthy",
            "database": "connected",
            "version": settings.version
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=503, detail="Service unavailable")


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
            "message": "An unexpected error occurred"
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
