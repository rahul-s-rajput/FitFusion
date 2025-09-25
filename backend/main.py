"""
FitFusion AI Workout App - FastAPI Backend
Main application entry point with all integrations
"""

import os
import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

# Import our services and middleware
from src.middleware.cors import setup_all_middleware
from src.utils.error_handler import setup_error_handlers
from src.services.database_service import initialize_database, close_database
from src.services.gemini_service import initialize_gemini

# Import API routers
from src.api.profile import router as profile_router
from src.api.equipment import router as equipment_router
from src.api.ai_generation import router as ai_generation_router
from src.api.programs import router as programs_router
from src.api.sessions import router as sessions_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application Lifecycle events"""
    # Startup
    print("Starting FitFusion API...")
    
    try:
        # Initialize database
        await initialize_database()
        print("Database initialized")
        
        # Initialize Gemini service
        initialize_gemini()
        print("Gemini AI service initialized")
        
        print("FitFusion API is ready!")
        
    except Exception as e:
        print(f"Failed to initialize services: {e}")
        raise
    
    yield
    
    # Shutdown
    print("Shutting down FitFusion API...")
    await close_database()
    print("Cleanup complete")

# Create FastAPI app
app = FastAPI(
    title="FitFusion AI Workout App",
    description="AI-powered personalized workout generation and tracking system",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan
)

# Setup middleware (CORS, security, logging, etc.)
setup_all_middleware(app)

# Setup error handlers
setup_error_handlers(app)

# Include API routers
app.include_router(profile_router, tags=["Profile"])
app.include_router(equipment_router, tags=["Equipment"])
app.include_router(ai_generation_router, tags=["AI Generation"])
app.include_router(programs_router, tags=["Programs"])
app.include_router(sessions_router, tags=["Sessions"])

# Root endpoints
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to FitFusion AI Workout App!",
        "version": "1.0.0",
        "docs": "/api/docs",
        "health": "/api/health"
    }

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    from src.services.database_service import get_database_service
    from src.services.gemini_service import get_gemini_service
    
    # Check database health
    db_service = get_database_service()
    db_health = await db_service.health_check()
    
    # Check Gemini health
    gemini_service = get_gemini_service()
    ai_health = await gemini_service.health_check()
    
    return {
        "status": "healthy",
        "service": "fitfusion-api",
        "version": "1.0.0",
        "database": db_health,
        "ai_service": ai_health,
        "environment": os.getenv("ENVIRONMENT", "development")
    }

@app.get("/api/info")
async def api_info():
    """API information endpoint"""
    return {
        "name": "FitFusion AI Workout App",
        "version": "1.0.0",
        "description": "AI-powered personalized workout generation and tracking",
        "features": [
            "AI Workout Generation with Gemini 2.5 Flash",
            "Equipment Management",
            "Progress Tracking", 
            "Offline-First Architecture",
            "Multi-Agent AI System",
            "Real-time Sync"
        ],
        "endpoints": {
            "profile": "/api/profile",
            "equipment": "/api/equipment", 
            "ai_generation": "/api/ai",
            "programs": "/api/programs",
            "sessions": "/api/sessions"
        }
    }

# Development server
if __name__ == "__main__":
    print("Starting FitFusion API in development mode...")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
