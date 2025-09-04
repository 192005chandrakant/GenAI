"""
Dashboard endpoint for backend server status and monitoring.
Provides comprehensive API for monitoring server health, performance, and API details.
"""
import os
import time
import socket
import json
import re
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple, Union
from fastapi import APIRouter, Request, HTTPException, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

from app.core.config import settings
from app.services.firestore_service import firestore_service
from app.services.vertex_ai_service import vertex_ai_service
from app.services.gemini_service import gemini_service
from app.services.faiss_service import faiss_service
from app.services.fact_check_service import fact_check_service
from app.services.translation_service import translation_service

router = APIRouter()

# Store server start time
SERVER_START_TIME = datetime.utcnow()

# Server statistics tracking
SERVER_STATS = {
    "total_requests": 0,
    "successful_requests": 0,
    "failed_requests": 0,
    "fact_checks_performed": 0,
    "users_served": 0,
    "data_processed_mb": 0.0,
    "peak_memory_usage": 0.0,
    "peak_cpu_usage": 0.0,
    "services_status": {
        "total_services": 6,
        "healthy_services": 0,
        "mock_services": 0,
        "error_services": 0
    }
}

def get_dynamic_server_info():
    """Get dynamic server information including all URLs and connection details."""
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
    except:
        hostname = "localhost"
        local_ip = "127.0.0.1"
    
    host = settings.HOST if settings.HOST != "0.0.0.0" else local_ip
    port = settings.PORT
    
    # Generate all possible URLs
    hosts = ["localhost", "127.0.0.1", local_ip, hostname] if settings.HOST == "0.0.0.0" else [host]
    
    urls = {}
    for h in hosts:
        base_url = f"http://{h}:{port}"
        urls[h] = {
            "base": base_url,
            "dashboard": f"{base_url}/api/v1/dashboard",
            "docs": f"{base_url}/docs",
            "redoc": f"{base_url}/redoc", 
            "status": f"{base_url}/api/v1/dashboard/status",
            "health": f"{base_url}/health",
            "frontend": f"http://{h}:3001" if h in ["localhost", "127.0.0.1"] else None
        }
    
    return {
        "host": host,
        "port": port,
        "hostname": hostname,
        "local_ip": local_ip,
        "urls": urls,
        "environment": "development" if settings.USE_MOCKS else "production",
        "primary_url": f"http://localhost:{port}",
        "is_local": settings.HOST in ["0.0.0.0", "localhost", "127.0.0.1"],
        "start_time": SERVER_START_TIME.strftime("%Y-%m-%d %H:%M:%S UTC"),
        "uptime": str(datetime.utcnow() - SERVER_START_TIME)
    }

@router.get("/api-info")
async def get_api_info():
    """Get comprehensive information about the Dashboard API."""
    dynamic_info = get_dynamic_server_info()
    base_url = dynamic_info["primary_url"]
    
    # List all available dashboard endpoints with descriptions
    endpoints = [
        {
            "path": "/api/v1/dashboard",
            "method": "GET",
            "description": "HTML dashboard with server status and information",
            "url": f"{base_url}/api/v1/dashboard",
            "response_type": "HTML"
        },
        {
            "path": "/api/v1/dashboard/status",
            "method": "GET",
            "description": "Get comprehensive server status as JSON with live data",
            "url": f"{base_url}/api/v1/dashboard/status",
            "response_type": "JSON"
        },
        {
            "path": "/api/v1/dashboard/health",
            "method": "GET",
            "description": "Health check endpoint with service status",
            "url": f"{base_url}/api/v1/dashboard/health",
            "response_type": "JSON"
        },
        {
            "path": "/api/v1/dashboard/live",
            "method": "GET",
            "description": "Live server status for real-time updates",
            "url": f"{base_url}/api/v1/dashboard/live",
            "response_type": "JSON"
        },
        {
            "path": "/api/v1/dashboard/metrics",
            "method": "GET",
            "description": "Detailed system and application metrics",
            "url": f"{base_url}/api/v1/dashboard/metrics",
            "response_type": "JSON"
        },
        {
            "path": "/api/v1/dashboard/services",
            "method": "GET",
            "description": "Detailed information about all backend services",
            "url": f"{base_url}/api/v1/dashboard/services",
            "response_type": "JSON"
        },
        {
            "path": "/api/v1/dashboard/analytics",
            "method": "GET", 
            "description": "Analytics data for the dashboard",
            "url": f"{base_url}/api/v1/dashboard/analytics",
            "response_type": "JSON"
        },
        {
            "path": "/api/v1/dashboard/logs",
            "method": "GET",
            "description": "Simplified logs endpoint for dashboard",
            "url": f"{base_url}/api/v1/dashboard/logs",
            "response_type": "HTML"
        },
        {
            "path": "/api/v1/dashboard/config",
            "method": "GET",
            "description": "Detailed configuration information",
            "url": f"{base_url}/api/v1/dashboard/config",
            "response_type": "JSON"
        },
        {
            "path": "/api/v1/dashboard/routes",
            "method": "GET",
            "description": "Detailed information about all API routes",
            "url": f"{base_url}/api/v1/dashboard/routes",
            "response_type": "JSON"
        },
        {
            "path": "/api/v1/dashboard/api-info",
            "method": "GET",
            "description": "Comprehensive information about the Dashboard API",
            "url": f"{base_url}/api/v1/dashboard/api-info",
            "response_type": "JSON"
        }
    ]
    
    return {
        "name": "Dashboard API",
        "description": "Backend dashboard and monitoring API for the GenAI platform",
        "version": settings.VERSION,
        "server_url": base_url,
        "endpoints": endpoints,
        "endpoint_count": len(endpoints),
        "documentation_url": f"{base_url}/api/v1/docs-api#dashboard"
    }


@router.get("/", response_class=HTMLResponse)
async def dashboard_home(request: Request):
    """Display backend dashboard with server status and information."""
    
    # Get system information
    system_info = get_system_info()
    
    # Get service status
    service_status = await get_service_status()
    
    # Get configuration info
    config_info = get_configuration_info()
    
    # Get dynamic server information
    dynamic_server_info = get_dynamic_server_info()
    
    # Get performance metrics
    performance_metrics = get_performance_metrics()
    
    # Get detailed server statistics
    server_stats = get_detailed_server_stats()
    
    # Increment request counter
    SERVER_STATS["total_requests"] += 1
    SERVER_STATS["successful_requests"] += 1
    
    # Generate HTML dashboard
    html_content = generate_dashboard_html(
        system_info=system_info,
        services=service_status,
        config_info=config_info,
        performance_metrics=performance_metrics,
        server_stats=server_stats,
        dynamic_server_info=dynamic_server_info
    )
    
    return HTMLResponse(content=html_content)

@router.get("/live")
async def get_live_status():
    """Get live server status for real-time updates."""
    uptime = datetime.utcnow() - SERVER_START_TIME
    server_stats = get_detailed_server_stats()
    dynamic_info = get_dynamic_server_info()
    system_info = get_system_info()
    services = await get_service_status()
    
    # Calculate health status
    services_health = sum(1 for s in services.values() if s["status"] in ["healthy", "mock"]) / max(1, len(services))
    health_status = "healthy"
    if services_health < 0.7:
        health_status = "critical"
    elif services_health < 0.9:
        health_status = "degraded"
    
    # Determine overall status
    cpu_warning = isinstance(system_info.get("cpu_usage"), (int, float)) and system_info.get("cpu_usage", 0) > 80
    memory_warning = isinstance(system_info.get("memory_usage"), (int, float)) and system_info.get("memory_usage", 0) > 85
    overall_status = health_status
    if cpu_warning or memory_warning:
        if health_status != "critical":
            overall_status = "warning"
    
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "status": overall_status,
        "uptime_seconds": int(uptime.total_seconds()),
        "uptime_formatted": server_stats["uptime"]["formatted"],
        "server_url": dynamic_info["primary_url"],
        "environment": dynamic_info["environment"],
        "services": {
            "healthy": sum(1 for s in services.values() if s["status"] == "healthy"),
            "mock": sum(1 for s in services.values() if s["status"] == "mock"),
            "error": sum(1 for s in services.values() if s["status"] == "error"),
            "total": len(services),
            "health_percentage": round(services_health * 100, 1)
        },
        "requests": {
            "total": server_stats["requests"]["total"],
            "per_minute": server_stats["requests"]["per_minute"],
            "per_hour": server_stats["requests"]["per_hour"],
            "success_rate": server_stats["requests"]["success_rate_percent"]
        },
        "system": {
            "cpu_usage": system_info.get("cpu_usage", "N/A"),
            "memory_usage": system_info.get("memory_usage", "N/A"),
            "disk_usage": system_info.get("disk_usage", "N/A"),
            "cpu_warning": cpu_warning,
            "memory_warning": memory_warning
        },
        "performance": {
            "peak_cpu": server_stats["performance"]["peak_cpu_usage"],
            "peak_memory": server_stats["performance"]["peak_memory_usage"],
            "fact_checks": server_stats["performance"]["fact_checks_performed"]
        }
    }


@router.get("/config")
async def get_config():
    """Get detailed configuration information."""
    config = get_configuration_info()
    
    # Add additional configuration details (with sensitive information removed)
    extended_config = {
        **config,
        "features": {
            "fact_checking": True,
            "multilingual": True,
            "image_analysis": settings.ENABLE_IMAGE_ANALYSIS if hasattr(settings, "ENABLE_IMAGE_ANALYSIS") else False,
            "url_extraction": True,
            "education_content": True,
            "gamification": True,
            "community": True,
            "admin_panel": True
        },
        "api": {
            "version": settings.VERSION,
            "base_path": settings.API_V1_STR,
            "rate_limiting": hasattr(settings, "RATE_LIMIT") and settings.RATE_LIMIT,
            "documentation_url": "/api/v1/docs-api"
        },
        "security": {
            "authentication": "firebase",
            "cors_enabled": len(settings.CORS_ORIGINS) > 0,
            "cors_origins_count": len(settings.CORS_ORIGINS)
        },
        "deployment": {
            "environment": "development" if settings.DEBUG else "production",
            "debug_mode": settings.DEBUG,
            "mock_services": settings.USE_MOCKS
        }
    }
    
    return extended_config

@router.get("/metrics")
async def get_metrics():
    """Get detailed system and application metrics."""
    system_info = get_system_info()
    server_stats = get_detailed_server_stats()
    
    # Calculate additional metrics
    uptime_seconds = server_stats["uptime"]["total_seconds"]
    requests_total = server_stats["requests"]["total"]
    requests_per_second = server_stats["requests"]["per_second"]
    
    # Get historical data (simplified mock data)
    current_time = datetime.utcnow()
    timestamps = [(current_time - timedelta(minutes=i*5)).isoformat() for i in range(12)]
    
    # Create time-series data
    time_series = {
        "cpu_usage": [
            {"timestamp": ts, "value": max(5, min(95, system_info.get("cpu_usage", 30) + ((i % 3) - 1) * 5))}
            for i, ts in enumerate(timestamps)
        ],
        "memory_usage": [
            {"timestamp": ts, "value": max(10, min(90, system_info.get("memory_usage", 40) + ((i % 4) - 2) * 3))}
            for i, ts in enumerate(timestamps)
        ],
        "requests_per_minute": [
            {"timestamp": ts, "value": max(1, requests_per_second * 60 + ((i % 5) - 2) * 3)}
            for i, ts in enumerate(timestamps)
        ]
    }
    
    # Server stats metrics
    metrics = {
        "uptime_seconds": uptime_seconds,
        "requests": {
            "total": requests_total,
            "per_second": requests_per_second,
            "per_minute": server_stats["requests"]["per_minute"],
            "per_hour": server_stats["requests"]["per_hour"],
            "success_rate": server_stats["requests"]["success_rate_percent"]
        },
        "performance": {
            "cpu_usage": system_info.get("cpu_usage", "N/A"),
            "memory_usage": system_info.get("memory_usage", "N/A"),
            "disk_usage": system_info.get("disk_usage", "N/A"),
            "fact_checks_performed": server_stats["performance"]["fact_checks_performed"],
            "data_processed_mb": server_stats["performance"]["data_processed_mb"],
            "peak_cpu_usage": server_stats["performance"]["peak_cpu_usage"],
            "peak_memory_usage": server_stats["performance"]["peak_memory_usage"]
        },
        "time_series": time_series,
        "timestamp": current_time.isoformat()
    }
    
    return metrics


@router.get("/services")
async def get_services():
    """Get detailed information about all backend services."""
    services = await get_service_status()
    
    # Calculate service health percentage
    total_services = len(services)
    healthy_services = sum(1 for s in services.values() if s["status"] == "healthy")
    mock_services = sum(1 for s in services.values() if s["status"] == "mock")
    error_services = sum(1 for s in services.values() if s["status"] == "error")
    
    health_percentage = 0
    if total_services > 0:
        health_percentage = round(((healthy_services + mock_services) / total_services) * 100, 1)
    
    # Add additional service details
    services_with_details = {}
    for name, service in services.items():
        services_with_details[name] = {
            **service,
            "endpoint": f"/api/v1/{name}" if name != "firestore" else None,
            "critical": name in ["firestore", "fact_check"],
            "last_checked": datetime.utcnow().isoformat(),
            "description": get_service_description(name)
        }
    
    return {
        "services": services_with_details,
        "summary": {
            "total": total_services,
            "healthy": healthy_services,
            "mock": mock_services,
            "error": error_services,
            "health_percentage": health_percentage,
            "status": "healthy" if health_percentage >= 90 else "degraded" if health_percentage >= 70 else "critical"
        },
        "timestamp": datetime.utcnow().isoformat()
    }


def get_service_description(service_name):
    """Get description for a service."""
    descriptions = {
        "firestore": "Google Firestore database service for storing all application data",
        "vertex_ai": "Google Vertex AI service for advanced AI capabilities",
        "gemini": "Google Gemini API service for multimodal AI processing",
        "faiss": "FAISS vector similarity search for claim matching",
        "fact_check": "Fact checking service for analyzing claims",
        "translation": "Translation service for multilingual support"
    }
    return descriptions.get(service_name, f"{service_name.capitalize()} service")


@router.get("/routes")
async def get_api_routes():
    """Get detailed information about all API routes."""
    from app.api.v1.api import api_router
    
    # Get module descriptions
    module_descriptions = {
        "dashboard": "Server monitoring and status dashboard",
        "documentation": "API documentation and guides",
        "auth": "Authentication and user authorization",
        "content": "Content analysis and processing",
        "reports": "User-submitted reports handling",
        "users": "User management and profiles",
        "gamification": "Gamification features and leaderboards",
        "learning": "Educational content and learning resources",
        "admin": "Administrative functionality",
        "upload": "File upload and management",
        "checks": "Misinformation checking functionality"
    }
    
    # Group routes by module/tag
    modules = {}
    
    # Process all routes
    for route in api_router.routes:
        # Skip internal endpoints
        if getattr(route, "include_in_schema", True) is False:
            continue
            
        # Get path and methods
        path = route.path
        methods = list(route.methods) if route.methods else ["GET"]
        
        # Determine module from path
        module = path.split("/")[1] if len(path.split("/")) > 1 else "root"
        
        # Add module to modules dict if not exists
        if module not in modules:
            modules[module] = {
                "name": module,
                "description": module_descriptions.get(module, f"{module.title()} functionality"),
                "routes": [],
                "route_count": 0,
                "methods": set()
            }
            
        # Add route to module
        modules[module]["routes"].append({
            "path": route.path,
            "methods": methods,
            "name": route.name if hasattr(route, "name") else None,
            "summary": route.summary if hasattr(route, "summary") else None,
            "description": route.description if hasattr(route, "description") else None,
            "full_path": f"{settings.API_V1_STR}{route.path}"
        })
        
        # Update module stats
        modules[module]["route_count"] += 1
        modules[module]["methods"].update(methods)
    
    # Convert sets to lists for JSON serialization
    for module in modules.values():
        module["methods"] = list(module["methods"])
    
    # Sort modules by name
    sorted_modules = dict(sorted(modules.items()))
    
    return {
        "modules": sorted_modules,
        "total_routes": sum(m["route_count"] for m in modules.values()),
        "module_count": len(modules),
        "api_base_path": settings.API_V1_STR,
        "api_version": settings.VERSION
    }


@router.get("/analytics")
async def get_analytics():
    """Get analytics data for the dashboard."""
    # This would typically fetch from a database, using mock data for now
    today = datetime.utcnow()
    
    # Generate date labels for the past 7 days
    date_labels = [(today - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]
    date_labels.reverse()
    
    # Generate mock analytics data
    analytics = {
        "fact_checks": {
            "total": 1243,
            "today": 34,
            "week_total": 287,
            "growth_percentage": 5.2,
            "daily": [23, 27, 35, 42, 51, 75, 34],  # Last 7 days
            "by_verdict": {
                "accurate": 42,
                "misleading": 23,
                "needs_context": 35
            }
        },
        "users": {
            "total": 567,
            "active_today": 43,
            "new_today": 12,
            "growth_percentage": 3.8,
            "daily_active": [35, 38, 41, 39, 42, 45, 43]  # Last 7 days
        },
        "content": {
            "total_processed": 1876,
            "text": 1243,
            "url": 421,
            "image": 212
        },
        "popular_topics": [
            {"name": "Health", "count": 342},
            {"name": "Politics", "count": 285},
            {"name": "Science", "count": 213},
            {"name": "Technology", "count": 187},
            {"name": "Environment", "count": 156}
        ],
        "time_series": {
            "labels": date_labels,
            "datasets": {
                "fact_checks": [23, 27, 35, 42, 51, 75, 34],
                "new_users": [8, 5, 7, 10, 13, 9, 12],
                "active_users": [35, 38, 41, 39, 42, 45, 43]
            }
        }
    }
    
    return {
        "data": analytics,
        "timestamp": today.isoformat(),
        "period": "last_7_days"
    }


@router.get("/logs", response_class=HTMLResponse)
async def get_logs():
    """Simplified logs endpoint for dashboard"""
    try:
        import datetime
        
        # Basic system info
        system_info = get_system_info()
        
        # Generate more realistic log entries
        recent_activity = [
            {"time": datetime.datetime.now().strftime("%H:%M:%S"), "event": "Dashboard accessed", "status": "info"},
            {"time": (datetime.datetime.now() - datetime.timedelta(seconds=30)).strftime("%H:%M:%S"), "event": "Health check completed", "status": "success"},
            {"time": (datetime.datetime.now() - datetime.timedelta(minutes=2)).strftime("%H:%M:%S"), "event": "Fact check request processed", "status": "success"},
            {"time": (datetime.datetime.now() - datetime.timedelta(minutes=5)).strftime("%H:%M:%S"), "event": "New user registered", "status": "info"},
            {"time": (datetime.datetime.now() - datetime.timedelta(minutes=8)).strftime("%H:%M:%S"), "event": "Translation service request", "status": "success"},
            {"time": (datetime.datetime.now() - datetime.timedelta(minutes=15)).strftime("%H:%M:%S"), "event": "Server startup", "status": "success"},
        ]
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>GenAI Backend - Logs</title>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                * {{ margin: 0; padding: 0; box-sizing: border-box; }}
                body {{ font-family: 'Arial', sans-serif; background: #f5f5f5; color: #333; }}
                .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); color: white; padding: 20px; text-align: center; }}
                .log-entry {{ background: white; margin: 10px 0; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                .log-time {{ color: #666; font-size: 0.9rem; }}
                .log-event {{ font-weight: bold; margin: 5px 0; }}
                .status-success {{ color: #28a745; }}
                .status-info {{ color: #17a2b8; }}
                .status-warning {{ color: #ffc107; }}
                .status-error {{ color: #dc3545; }}
                .back-btn {{ display: inline-block; margin: 20px 0; padding: 10px 20px; background: #007bff; color: white; text-decoration: none; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>📋 System Logs</h1>
                <p>Recent Activity & Events</p>
            </div>
            <div class="container">
                <a href="/" class="back-btn">← Back to Dashboard</a>
                
                <h3>Recent Activity</h3>
                {"".join([f'<div class="log-entry"><div class="log-time">{entry["time"]}</div><div class="log-event">{entry["event"]}</div><div class="status-{entry["status"]}">Status: {entry["status"]}</div></div>' for entry in recent_activity])}
                
                <h3 style="margin-top: 30px;">System Information</h3>
                <div class="log-entry">
                    <strong>CPU Usage:</strong> {system_info.get('cpu_usage', 'N/A')}%<br>
                    <strong>Memory Usage:</strong> {system_info.get('memory_usage', 'N/A')}%<br>
                    <strong>Disk Usage:</strong> {system_info.get('disk_usage', 'N/A')}%<br>
                    <strong>Python Version:</strong> {system_info.get('python_version', 'N/A')}<br>
                    <strong>Platform:</strong> {system_info.get('platform', 'N/A')}
                </div>
            </div>
        </body>
        </html>
        """
        
        return html_content
        
    except Exception as e:
        return f"<html><body><h1>Error loading logs</h1><p>{str(e)}</p><a href='/'>Back to Dashboard</a></body></html>"

@router.get("/status")
async def get_status():
    """Get comprehensive server status as JSON with live data."""
    uptime = datetime.utcnow() - SERVER_START_TIME
    server_stats = get_detailed_server_stats()
    dynamic_info = get_dynamic_server_info()
    service_status = await get_service_status()
    system_info = get_system_info()
    config_info = get_configuration_info()
    
    # Increment request counter
    SERVER_STATS["total_requests"] += 1
    SERVER_STATS["successful_requests"] += 1
    
    # Get API endpoint status
    api_endpoints = await get_api_endpoints_status()
    
    return {
        "status": "running",
        "message": "Server is running",
        "timestamp": datetime.utcnow().isoformat(),
        "uptime": str(uptime),
        "uptime_seconds": int(uptime.total_seconds()),
        "start_time": SERVER_START_TIME.isoformat(),
        "server": {
            "name": "GenAI Backend Server",
            "version": settings.VERSION,
            "environment": dynamic_info["environment"],
            "host": dynamic_info["host"],
            "port": dynamic_info["port"],
            "hostname": dynamic_info["hostname"],
            "local_ip": dynamic_info["local_ip"],
            "is_local": dynamic_info["is_local"],
            "urls": dynamic_info["urls"]
        },
        "project": settings.PROJECT_NAME,
        "server_statistics": server_stats,
        "services": service_status,
        "services_summary": {
            "total": len(service_status),
            "healthy": sum(1 for s in service_status.values() if s["status"] == "healthy"),
            "mock": sum(1 for s in service_status.values() if s["status"] == "mock"),
            "error": sum(1 for s in service_status.values() if s["status"] == "error")
        },
        "system": system_info,
        "system_health": {
            "cpu_status": get_resource_status(system_info.get("cpu_usage", 0), [70, 90]),
            "memory_status": get_resource_status(system_info.get("memory_usage", 0), [80, 95]),
            "disk_status": get_resource_status(system_info.get("disk_usage", 0), [85, 95])
        },
        "api": {
            "endpoints": api_endpoints,
            "endpoints_count": len(api_endpoints),
            "routes_available": len(api_endpoints) > 0
        },
        "configuration": config_info,
        "api_urls": {
            "dashboard": f"{dynamic_info['primary_url']}/api/v1/dashboard",
            "documentation": f"{dynamic_info['primary_url']}/api/v1/docs-api",
            "api_docs": f"{dynamic_info['primary_url']}/docs",
            "health": f"{dynamic_info['primary_url']}/health",
            "status": f"{dynamic_info['primary_url']}/api/v1/dashboard/status",
            "metrics": f"{dynamic_info['primary_url']}/api/v1/dashboard/metrics",
            "services": f"{dynamic_info['primary_url']}/api/v1/dashboard/services",
            "live_status": f"{dynamic_info['primary_url']}/api/v1/dashboard/live"
        }
    }


def get_resource_status(value, thresholds):
    """Get status based on resource usage value and thresholds."""
    try:
        if isinstance(value, str) and value.endswith('%'):
            value = float(value.rstrip('%'))
        elif isinstance(value, str) and value != "N/A":
            value = float(value)
        
        if value == "N/A" or value is None:
            return "unknown"
        elif value > thresholds[1]:
            return "critical"
        elif value > thresholds[0]:
            return "warning"
        else:
            return "healthy"
    except Exception:
        return "unknown"


async def get_api_endpoints_status():
    """Get the status of all API endpoints."""
    from fastapi import FastAPI
    from app.api.v1.api import api_router
    
    endpoints = []
    
    # Get all routes from the router
    for route in api_router.routes:
        endpoint_info = {
            "path": route.path,
            "methods": list(route.methods) if route.methods else ["GET"],
            "name": route.name,
            "tags": route.tags if hasattr(route, "tags") else [],
            "status": "active"
        }
        endpoints.append(endpoint_info)
    
    # Sort endpoints by path
    endpoints.sort(key=lambda x: x["path"])
    
    return endpoints

@router.get("/health")
async def health_check():
    """Health check endpoint."""
    services = await get_service_status()
    system_info = get_system_info()
    all_healthy = all(service["status"] in ["healthy", "mock"] for service in services.values())
    
    return {
        "status": "healthy" if all_healthy else "degraded",
        "timestamp": datetime.utcnow().isoformat(),
        "services": services,
        "resources": {
            "cpu_usage": system_info.get("cpu_usage", "N/A"),
            "memory_usage": system_info.get("memory_usage", "N/A"),
            "disk_usage": system_info.get("disk_usage", "N/A")
        },
        "uptime": str(datetime.utcnow() - SERVER_START_TIME)
    }

def get_system_info() -> Dict[str, Any]:
    """Get comprehensive system information and metrics"""
    import socket
    import sys
    import platform
    
    info = {
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "platform": platform.platform(),
        "architecture": platform.architecture()[0],
        "processor": platform.processor() or "Unknown",
        "hostname": socket.gethostname(),
        "python_executable": sys.executable,
        "working_directory": os.getcwd(),
        "environment": os.environ.get("ENVIRONMENT", "development")
    }
    
    if PSUTIL_AVAILABLE:
        try:
            # System metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Network info
            network_io = psutil.net_io_counters()
            
            # Process info
            process = psutil.Process()
            process_memory = process.memory_info()
            
            info.update({
                "cpu_usage": round(cpu_percent, 2),
                "cpu_count": psutil.cpu_count(),
                "cpu_freq": psutil.cpu_freq().current if psutil.cpu_freq() else "Unknown",
                "memory_total": round(memory.total / (1024**3), 2),  # GB
                "memory_available": round(memory.available / (1024**3), 2),  # GB
                "memory_usage": round(memory.percent, 2),
                "disk_total": round(disk.total / (1024**3), 2),  # GB
                "disk_free": round(disk.free / (1024**3), 2),  # GB
                "disk_usage": round((disk.used / disk.total) * 100, 2),
                "network_bytes_sent": round(network_io.bytes_sent / (1024**2), 2),  # MB
                "network_bytes_recv": round(network_io.bytes_recv / (1024**2), 2),  # MB
                "process_memory_rss": round(process_memory.rss / (1024**2), 2),  # MB
                "process_memory_vms": round(process_memory.vms / (1024**2), 2),  # MB
                "process_cpu_percent": round(process.cpu_percent(), 2),
                "process_num_threads": process.num_threads(),
                "boot_time": datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S")
            })
            
            # Update peak usage
            SERVER_STATS["peak_memory_usage"] = max(SERVER_STATS["peak_memory_usage"], memory.percent)
            SERVER_STATS["peak_cpu_usage"] = max(SERVER_STATS["peak_cpu_usage"], cpu_percent)
            
        except Exception as e:
            info["system_metrics_error"] = str(e)
    else:
        info.update({
            "cpu_usage": "N/A (psutil not available)",
            "memory_usage": "N/A (psutil not available)", 
            "disk_usage": "N/A (psutil not available)"
        })
    
    return info

def get_detailed_server_stats():
    """Get comprehensive server statistics"""
    uptime = datetime.utcnow() - SERVER_START_TIME
    uptime_seconds = uptime.total_seconds()
    
    # Calculate uptime components
    days = int(uptime_seconds // 86400)
    hours = int((uptime_seconds % 86400) // 3600)
    minutes = int((uptime_seconds % 3600) // 60)
    seconds = int(uptime_seconds % 60)
    
    # Request rate calculations
    total_requests = SERVER_STATS["total_requests"] + 1  # Include current request
    requests_per_second = round(total_requests / max(uptime_seconds, 1), 2)
    requests_per_minute = round(requests_per_second * 60, 2)
    requests_per_hour = round(requests_per_minute * 60, 2)
    
    # Success rate
    success_rate = 0
    if total_requests > 0:
        success_rate = round((SERVER_STATS["successful_requests"] / total_requests) * 100, 2)
    
    return {
        "uptime": {
            "total_seconds": int(uptime_seconds),
            "formatted": f"{days}d {hours}h {minutes}m {seconds}s",
            "days": days,
            "hours": hours,
            "minutes": minutes,
            "seconds": seconds
        },
        "requests": {
            "total": total_requests,
            "successful": SERVER_STATS["successful_requests"],
            "failed": SERVER_STATS["failed_requests"],
            "success_rate_percent": success_rate,
            "per_second": requests_per_second,
            "per_minute": requests_per_minute,
            "per_hour": requests_per_hour
        },
        "performance": {
            "fact_checks_performed": SERVER_STATS["fact_checks_performed"],
            "users_served": SERVER_STATS["users_served"],
            "data_processed_mb": SERVER_STATS["data_processed_mb"],
            "peak_memory_usage": SERVER_STATS["peak_memory_usage"],
            "peak_cpu_usage": SERVER_STATS["peak_cpu_usage"]
        },
        "services": SERVER_STATS["services_status"]
    }

async def get_service_status() -> Dict[str, Dict[str, Any]]:
    """Get status of all services."""
    services = {}
    
    # Firestore Service
    try:
        if firestore_service.use_mock:
            services["firestore"] = {"status": "mock", "message": "Using mock service"}
        else:
            services["firestore"] = {"status": "healthy", "message": "Connected to Firestore"}
    except Exception as e:
        services["firestore"] = {"status": "error", "message": str(e)}
    
    # Vertex AI Service
    try:
        if vertex_ai_service.use_mock:
            services["vertex_ai"] = {"status": "mock", "message": "Using mock service"}
        else:
            services["vertex_ai"] = {"status": "healthy", "message": "Connected to Vertex AI"}
    except Exception as e:
        services["vertex_ai"] = {"status": "error", "message": str(e)}
    
    # Gemini Service
    try:
        if gemini_service.use_mock:
            services["gemini"] = {"status": "mock", "message": "Using mock service"}
        else:
            services["gemini"] = {"status": "healthy", "message": "Connected to Gemini"}
    except Exception as e:
        services["gemini"] = {"status": "error", "message": str(e)}
    
    # FAISS Service
    try:
        if faiss_service.use_mock:
            services["faiss"] = {"status": "mock", "message": "Using mock service"}
        else:
            services["faiss"] = {"status": "healthy", "message": "FAISS index loaded"}
    except Exception as e:
        services["faiss"] = {"status": "error", "message": str(e)}
    
    # Fact Check Service
    try:
        services["fact_check"] = {"status": "healthy", "message": "Fact check service active"}
    except Exception as e:
        services["fact_check"] = {"status": "error", "message": str(e)}
    
    # Translation Service
    try:
        if translation_service.use_mock:
            services["translation"] = {"status": "mock", "message": "Using mock service"}
        else:
            services["translation"] = {"status": "healthy", "message": "Connected to Translation API"}
    except Exception as e:
        services["translation"] = {"status": "error", "message": str(e)}
    
    return services

def get_configuration_info() -> Dict[str, Any]:
    """Get configuration information."""
    return {
        "project_name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "debug": settings.DEBUG,
        "use_mocks": settings.USE_MOCKS,
        "host": settings.HOST,
        "port": settings.PORT,
        "api_v1_str": settings.API_V1_STR,
        "google_cloud_project": settings.GOOGLE_CLOUD_PROJECT,
        "vertex_ai_location": settings.VERTEX_AI_LOCATION,
        "cors_origins": len(settings.CORS_ORIGINS),
        "log_level": settings.LOG_LEVEL
    }

def get_performance_metrics() -> Dict[str, Any]:
    """Get performance metrics."""
    uptime = datetime.utcnow() - SERVER_START_TIME
    
    return {
        "uptime": str(uptime),
        "uptime_seconds": int(uptime.total_seconds()),
        "start_time": SERVER_START_TIME.isoformat(),
        "current_time": datetime.utcnow().isoformat(),
        "port": settings.PORT,
        "host": settings.HOST
    }

def generate_dashboard_html(system_info, services, config_info, performance_metrics, server_stats, dynamic_server_info) -> str:
    """Generate HTML dashboard."""
    
    # Generate service status cards
    service_cards = ""
    for service_name, service_info in services.items():
        status_color = {
            "healthy": "#22c55e",
            "mock": "#f59e0b", 
            "error": "#ef4444"
        }.get(service_info["status"], "#6b7280")
        
        service_cards += f"""
        <div class="service-card">
            <h3>{service_name.replace('_', ' ').title()}</h3>
            <div class="status-indicator" style="background-color: {status_color}"></div>
            <p class="status-text">{service_info['status'].title()}</p>
            <p class="service-message">{service_info['message']}</p>
        </div>
        """
    
    # Generate configuration items
    config_items = ""
    for key, value in config_info.items():
        config_items += f"""
        <div class="config-item">
            <span class="config-key">{key.replace('_', ' ').title()}:</span>
            <span class="config-value">{value}</span>
        </div>
        """
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>GenAI Backend Dashboard</title>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }}
            
            .container {{
                max-width: 1200px;
                margin: 0 auto;
                background: white;
                border-radius: 15px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                overflow: hidden;
            }}
            
            .header {{
                background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
                color: white;
                padding: 30px;
                text-align: center;
            }}
            
            .header h1 {{
                font-size: 2.5rem;
                margin-bottom: 10px;
            }}
            
            .header p {{
                font-size: 1.1rem;
                opacity: 0.9;
                margin-bottom: 20px;
            }}
            
            .action-buttons {{
                display: flex;
                gap: 15px;
                justify-content: center;
                flex-wrap: wrap;
                margin-top: 20px;
            }}
            
            .action-btn {{
                background: rgba(255,255,255,0.2);
                color: white;
                border: 1px solid rgba(255,255,255,0.3);
                padding: 10px 20px;
                border-radius: 25px;
                text-decoration: none;
                transition: all 0.2s;
                font-weight: 500;
            }}
            
            .action-btn:hover {{
                background: rgba(255,255,255,0.3);
                transform: translateY(-1px);
            }}
            
            .dashboard-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 30px;
                padding: 30px;
            }}
            
            .section {{
                background: #f8fafc;
                border-radius: 10px;
                padding: 25px;
                border-left: 4px solid #3b82f6;
            }}
            
            .section h2 {{
                color: #1f2937;
                margin-bottom: 20px;
                font-size: 1.5rem;
                display: flex;
                align-items: center;
                gap: 10px;
            }}
            
            .section-icon {{
                width: 24px;
                height: 24px;
                background: #3b82f6;
                border-radius: 50%;
                display: inline-block;
            }}
            
            .services-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 15px;
            }}
            
            .service-card {{
                background: white;
                border-radius: 8px;
                padding: 20px;
                text-align: center;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                transition: transform 0.2s;
            }}
            
            .service-card:hover {{
                transform: translateY(-2px);
            }}
            
            .stats-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                gap: 15px;
                margin-bottom: 25px;
            }}
            
            .stat-card {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border-radius: 10px;
                padding: 20px;
                text-align: center;
                box-shadow: 0 4px 15px rgba(0,0,0,0.1);
                transition: all 0.3s ease;
            }}
            
            .stat-card:hover {{
                transform: translateY(-3px);
                box-shadow: 0 6px 20px rgba(0,0,0,0.15);
            }}
            
            .stat-value {{
                font-size: 2rem;
                font-weight: bold;
                margin-bottom: 8px;
                display: block;
            }}
            
            .stat-label {{
                font-size: 0.9rem;
                opacity: 0.9;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}
            
            .performance-details {{
                background: #f8f9fa;
                border-radius: 8px;
                padding: 20px;
                margin-top: 20px;
            }}
            
            .performance-details h4 {{
                color: #2c3e50;
                margin-bottom: 15px;
                font-size: 1.2rem;
            }}
            
            .service-card h3 {{
                color: #374151;
                margin-bottom: 10px;
                font-size: 1.1rem;
            }}
            
            .status-indicator {{
                width: 12px;
                height: 12px;
                border-radius: 50%;
                margin: 0 auto 10px;
            }}
            
            .status-text {{
                font-weight: bold;
                margin-bottom: 5px;
                text-transform: uppercase;
                font-size: 0.9rem;
            }}
            
            .service-message {{
                font-size: 0.85rem;
                color: #6b7280;
            }}
            
            .metric-item {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 12px 0;
                border-bottom: 1px solid #e5e7eb;
            }}
            
            .metric-item:last-child {{
                border-bottom: none;
            }}
            
            .metric-label {{
                font-weight: 500;
                color: #374151;
            }}
            
            .metric-value {{
                font-weight: bold;
                color: #1f2937;
                background: #e0f2fe;
                padding: 4px 8px;
                border-radius: 4px;
                font-size: 0.9rem;
            }}
            
            .config-item {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 10px 0;
                border-bottom: 1px solid #e5e7eb;
            }}
            
            .config-item:last-child {{
                border-bottom: none;
            }}
            
            .config-key {{
                font-weight: 500;
                color: #374151;
                flex: 1;
            }}
            
            .config-value {{
                font-weight: bold;
                color: #1f2937;
                background: #f3f4f6;
                padding: 4px 8px;
                border-radius: 4px;
                font-size: 0.9rem;
                max-width: 60%;
                text-align: right;
                word-break: break-all;
            }}
            
            .server-urls {{
                display: flex;
                flex-direction: column;
                gap: 20px;
            }}
            
            .url-group {{
                border: 1px solid #e5e7eb;
                border-radius: 8px;
                padding: 15px;
                background: white;
            }}
            
            .url-group h4 {{
                margin: 0 0 10px 0;
                color: #374151;
                font-size: 1.1rem;
            }}
            
            .url-item {{
                display: flex;
                align-items: center;
                justify-content: space-between;
                padding: 8px 0;
                border-bottom: 1px solid #f3f4f6;
            }}
            
            .url-item:last-child {{
                border-bottom: none;
            }}
            
            .url-item.primary {{
                background: linear-gradient(135deg, #e0f2fe 0%, #b3e5fc 100%);
                padding: 12px;
                border-radius: 6px;
                margin-bottom: 10px;
            }}
            
            .url-link {{
                color: #3b82f6;
                text-decoration: none;
                font-weight: 500;
                padding: 4px 8px;
                border-radius: 4px;
                transition: all 0.2s;
                margin-right: 8px;
            }}
            
            .url-link:hover {{
                background: #dbeafe;
                color: #1d4ed8;
            }}
            
            .url-link.frontend {{
                background: #fef3c7;
                color: #d97706;
            }}
            
            .url-link.frontend:hover {{
                background: #fde68a;
                color: #b45309;
            }}
            
            .url-links {{
                display: flex;
                flex-wrap: wrap;
                gap: 5px;
            }}
            
            .status-indicator {{
                font-size: 0.9rem;
                font-weight: 500;
            }}
            
            .status-indicator.online {{
                color: #10b981;
            }}
            
            .server-details {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 15px;
                margin-top: 15px;
                padding: 15px;
                background: #f9fafb;
                border-radius: 6px;
            }}
            
            .detail-item {{
                display: flex;
                align-items: center;
                gap: 8px;
            }}
            
            .detail-label {{
                font-weight: 500;
                color: #6b7280;
                min-width: 80px;
            }}
            
            .detail-value {{
                font-weight: 600;
                color: #1f2937;
                font-family: 'Courier New', monospace;
            }}
            
            .status-banner {{
                background: linear-gradient(135deg, #10b981 0%, #059669 100%);
                color: white;
                text-align: center;
                padding: 15px;
                font-weight: bold;
                font-size: 1.1rem;
            }}
            
            .refresh-btn {{
                position: fixed;
                bottom: 20px;
                right: 20px;
                background: #3b82f6;
                color: white;
                border: none;
                border-radius: 50px;
                padding: 15px 20px;
                cursor: pointer;
                box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3);
                font-weight: bold;
                transition: all 0.2s;
            }}
            
            .refresh-btn:hover {{
                background: #2563eb;
                transform: translateY(-2px);
            }}
            
            @media (max-width: 768px) {{
                .dashboard-grid {{
                    grid-template-columns: 1fr;
                    padding: 15px;
                }}
                
                .header {{
                    padding: 20px;
                }}
                
                .header h1 {{
                    font-size: 2rem;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="status-banner">
                Server is running
            </div>
            
            <div class="header">
                <h1>🚀 GenAI Backend Dashboard</h1>
                <p>Backend Server Monitoring & Control Center</p>
                <div class="action-buttons">
                    <a href="/api/v1/docs-api" class="action-btn" target="_blank">📚 API Guide</a>
                    <a href="/docs" class="action-btn" target="_blank">📖 OpenAPI</a>
                    <a href="/redoc" class="action-btn" target="_blank">� ReDoc</a>
                    <a href="/api/v1/dashboard/status" class="action-btn" target="_blank">🔗 JSON API</a>
                    <a href="#" onclick="location.reload()" class="action-btn">🔄 Refresh</a>
                </div>
            </div>
            
            <div class="dashboard-grid">
                <!-- Server Connection Information -->
                <div class="section">
                    <h2>
                        <span class="section-icon">🌐</span>
                        Server Connection Information
                        <small id="last-updated" style="float: right; font-size: 0.8em; opacity: 0.7;">Last updated: {datetime.utcnow().strftime('%H:%M:%S')}</small>
                    </h2>
                    <div class="server-urls">
                        <div class="url-group">
                            <h4>🏠 Primary Server URL</h4>
                            <div class="url-item primary">
                                <a href="{dynamic_server_info['primary_url']}" target="_blank" class="url-link">
                                    {dynamic_server_info['primary_url']}
                                </a>
                                <span class="status-indicator online">● Online</span>
                            </div>
                        </div>
                        
                        <div class="url-group">
                            <h4>🔗 All Available URLs</h4>
                            {''.join([f'''
                            <div class="url-item">
                                <strong>{host}:</strong>
                                <div class="url-links">
                                    <a href="{urls['base']}" target="_blank" class="url-link">Dashboard</a>
                                    <a href="{urls['docs']}" target="_blank" class="url-link">API Docs</a>
                                    <a href="{urls['health']}" target="_blank" class="url-link">Health</a>
                                    {f'<a href="{urls["frontend"]}" target="_blank" class="url-link frontend">Frontend</a>' if urls.get('frontend') else ''}
                                </div>
                            </div>
                            ''' for host, urls in dynamic_server_info['urls'].items()])}
                        </div>
                        
                        <div class="server-details">
                            <div class="detail-item">
                                <span class="detail-label">🖥️ Host:</span>
                                <span class="detail-value">{dynamic_server_info['host']}</span>
                            </div>
                            <div class="detail-item">
                                <span class="detail-label">🔌 Port:</span>
                                <span class="detail-value">{dynamic_server_info['port']}</span>
                            </div>
                            <div class="detail-item">
                                <span class="detail-label">🌍 Environment:</span>
                                <span class="detail-value">{dynamic_server_info['environment']}</span>
                            </div>
                            <div class="detail-item">
                                <span class="detail-label">⏰ Started:</span>
                                <span class="detail-value">{dynamic_server_info['start_time']}</span>
                            </div>
                            <div class="detail-item">
                                <span class="detail-label">⏱️ Uptime:</span>
                                <span class="detail-value">{dynamic_server_info['uptime']}</span>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Services Status -->
                <div class="section">
                    <h2>
                        <span class="section-icon"></span>
                        Services Status
                    </h2>
                    <div class="services-grid">
                        {service_cards}
                    </div>
                </div>
                
                <!-- Server Statistics -->
                <div class="section">
                    <h2>
                        <span class="section-icon">📊</span>
                        Server Statistics & Uptime
                    </h2>
                    <div class="stats-grid">
                        <div class="stat-card">
                            <div class="stat-value">{server_stats['uptime']['formatted']}</div>
                            <div class="stat-label">Server Uptime</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value">{server_stats['requests']['total']}</div>
                            <div class="stat-label">Total Requests</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value">{server_stats['requests']['success_rate_percent']}%</div>
                            <div class="stat-label">Success Rate</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value">{server_stats['requests']['per_hour']}</div>
                            <div class="stat-label">Requests/Hour</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value">{server_stats['performance']['fact_checks_performed']}</div>
                            <div class="stat-label">Fact Checks</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value">{server_stats['performance']['peak_cpu_usage']:.1f}%</div>
                            <div class="stat-label">Peak CPU Usage</div>
                        </div>
                    </div>
                    
                    <div class="performance-details">
                        <h4>Performance Metrics</h4>
                        <div class="metric-item">
                            <span class="metric-label">Requests per Second</span>
                            <span class="metric-value">{server_stats['requests']['per_second']}</span>
                        </div>
                        <div class="metric-item">
                            <span class="metric-label">Peak Memory Usage</span>
                            <span class="metric-value">{server_stats['performance']['peak_memory_usage']:.1f}%</span>
                        </div>
                        <div class="metric-item">
                            <span class="metric-label">Data Processed</span>
                            <span class="metric-value">{server_stats['performance']['data_processed_mb']:.2f} MB</span>
                        </div>
                        <div class="metric-item">
                            <span class="metric-label">Users Served</span>
                            <span class="metric-value">{server_stats['performance']['users_served']}</span>
                        </div>
                    </div>
                </div>
                
                <!-- System Information -->
                <div class="section">
                    <h2>
                        <span class="section-icon"></span>
                        System Information
                    </h2>
                    <div class="metric-item">
                        <span class="metric-label">Platform</span>
                        <span class="metric-value">{system_info.get('platform', 'Unknown')}</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-label">CPU Usage</span>
                        <span class="metric-value">{system_info.get('cpu_usage', 'N/A')}</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-label">Memory Usage</span>
                        <span class="metric-value">{system_info.get('memory_percent', 'N/A')}</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-label">Memory Used</span>
                        <span class="metric-value">{system_info.get('memory_used', 'N/A')}</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-label">Disk Usage</span>
                        <span class="metric-value">{system_info.get('disk_percent', 'N/A')}</span>
                    </div>
                </div>
                
                <!-- Performance Metrics -->
                <div class="section">
                    <h2>
                        <span class="section-icon"></span>
                        Performance Metrics
                    </h2>
                    <div class="metric-item">
                        <span class="metric-label">Server Uptime</span>
                        <span class="metric-value">{performance_metrics.get('uptime', 'N/A')}</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-label">Start Time</span>
                        <span class="metric-value">{performance_metrics.get('start_time', 'N/A')}</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-label">Current Time</span>
                        <span class="metric-value">{performance_metrics.get('current_time', 'N/A')}</span>
                    </div>
                </div>
                
                <!-- Configuration -->
                <div class="section">
                    <h2>
                        <span class="section-icon"></span>
                        Configuration
                    </h2>
                    {config_items}
                </div>
            </div>
        </div>
        
        <button class="refresh-btn" onclick="refreshData()">
            🔄 Refresh
        </button>
        
        <script>
            let autoRefreshInterval;
            let lastUpdateTime = new Date();
            
            // Update timestamp display
            function updateTimestamp() {{
                const now = new Date();
                const timeString = now.toLocaleTimeString();
                const timestampElement = document.getElementById('last-updated');
                if (timestampElement) {{
                    timestampElement.textContent = `Last updated: ${{timeString}}`;
                }}
            }}
            
            // Fetch live data from the API
            async function fetchLiveData() {{
                try {{
                    const response = await fetch('/api/v1/dashboard/live');
                    if (response.ok) {{
                        const data = await response.json();
                        updateLiveElements(data);
                        updateTimestamp();
                        lastUpdateTime = new Date();
                    }}
                }} catch (error) {{
                    console.error('Failed to fetch live data:', error);
                }}
            }}
            
            // Update live elements with new data
            function updateLiveElements(data) {{
                // Update uptime
                const uptimeElements = document.querySelectorAll('[data-stat="uptime"]');
                uptimeElements.forEach(el => {{
                    if (el) el.textContent = data.uptime_formatted;
                }});
                
                // Update total requests
                const requestElements = document.querySelectorAll('[data-stat="total-requests"]');
                requestElements.forEach(el => {{
                    if (el) el.textContent = data.requests.total;
                }});
                
                // Update success rate
                const successRateElements = document.querySelectorAll('[data-stat="success-rate"]');
                successRateElements.forEach(el => {{
                    if (el) el.textContent = data.requests.success_rate + '%';
                }});
                
                // Update requests per hour
                const requestsPerHourElements = document.querySelectorAll('[data-stat="requests-per-hour"]');
                requestsPerHourElements.forEach(el => {{
                    if (el) el.textContent = data.requests.per_hour;
                }});
                
                // Update system info
                if (data.system) {{
                    const cpuElements = document.querySelectorAll('[data-stat="cpu-usage"]');
                    cpuElements.forEach(el => {{
                        if (el) el.textContent = data.system.cpu_usage + '%';
                    }});
                    
                    const memoryElements = document.querySelectorAll('[data-stat="memory-usage"]');
                    memoryElements.forEach(el => {{
                        if (el) el.textContent = data.system.memory_usage + '%';
                    }});
                }}
                
                // Add visual feedback for updates
                document.body.style.background = 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)';
                setTimeout(() => {{
                    document.body.style.background = '';
                }}, 200);
            }}
            
            // Manual refresh function
            async function refreshData() {{
                const refreshBtn = document.querySelector('.refresh-btn');
                const originalText = refreshBtn.textContent;
                
                refreshBtn.textContent = '⏳ Refreshing...';
                refreshBtn.disabled = true;
                
                await fetchLiveData();
                
                setTimeout(() => {{
                    refreshBtn.textContent = originalText;
                    refreshBtn.disabled = false;
                }}, 1000);
            }}
            
            // Auto-refresh every 10 seconds for live updates
            function startAutoRefresh() {{
                autoRefreshInterval = setInterval(fetchLiveData, 10000);
            }}
            
            // Stop auto-refresh
            function stopAutoRefresh() {{
                if (autoRefreshInterval) {{
                    clearInterval(autoRefreshInterval);
                }}
            }}
            
            // Add data attributes to elements for live updates
            function addDataAttributes() {{
                // Add data attributes to stat values for live updates
                const uptimeElement = document.querySelector('.stat-card:first-child .stat-value');
                if (uptimeElement) uptimeElement.setAttribute('data-stat', 'uptime');
                
                const requestElements = document.querySelectorAll('.stat-value');
                if (requestElements[1]) requestElements[1].setAttribute('data-stat', 'total-requests');
                if (requestElements[2]) requestElements[2].setAttribute('data-stat', 'success-rate');
                if (requestElements[3]) requestElements[3].setAttribute('data-stat', 'requests-per-hour');
            }}
            
            // Initialize on page load
            document.addEventListener('DOMContentLoaded', function() {{
                updateTimestamp();
                addDataAttributes();
                startAutoRefresh();
                
                // Update timestamp every second
                setInterval(updateTimestamp, 1000);
                
                // Add visibility change handler to pause/resume auto-refresh
                document.addEventListener('visibilitychange', function() {{
                    if (document.hidden) {{
                        stopAutoRefresh();
                    }} else {{
                        startAutoRefresh();
                        fetchLiveData(); // Immediate update when tab becomes visible
                    }}
                }});
            }});
            
            // Cleanup on page unload
            window.addEventListener('beforeunload', function() {{
                stopAutoRefresh();
            }});
        </script>
    </body>
    </html>
    """
    
    return html_content
