from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Import routers
from .api import auth_routes, roadmap_routes

# Create FastAPI app
app = FastAPI(
    title="GBLMS API",
    description="Goal-Based Learning Management System - Backend API with Scout Integration",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
allowed_origins = [
    frontend_url,
    "http://localhost:5173",
    "http://localhost:3000",
    "https://*.vercel.app",  # Allow all Vercel preview deployments
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_routes.router)
app.include_router(roadmap_routes.router)

@app.get("/")
async def root():
    """Root endpoint - API status check."""
    return {
        "service": "GBLMS API",
        "status": "running",
        "version": "1.0.0",
        "features": {
            "scout": "enabled",
            "auth": "simple",
            "databases": {
                "supabase": os.getenv("SUPABASE_URL") is not None,
                "neo4j": os.getenv("NEO4J_URI") is not None,
                "redis": os.getenv("REDIS_URL") is not None
            }
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "google_api_configured": bool(os.getenv("GOOGLE_API_KEY"))
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")

    uvicorn.run(
        "src.main:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )
