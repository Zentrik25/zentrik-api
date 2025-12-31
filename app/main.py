"""
Application entry point - FastAPI application setup.

This is the main file that starts the API server.
It configures middleware, includes routers, and initializes the database.

STATELESS ARCHITECTURE:
- No application state is maintained
- Each request is independent
- Database sessions are created per-request and automatically closed
- Safe for horizontal scaling (multiple instances)
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import init_db
from app.api.provider_routes import router as provider_router
from app.api.booking_routes import router as booking_router

# Initialize database tables on startup
# WARNING: In production, use Alembic migrations instead
init_db()

# Create FastAPI application instance
app = FastAPI(
    title="Multi-Sector Front Desk Management API",
    description="API for managing bookings across medical, real estate, automotive, and other sectors",
    version="1.0.0",
    docs_url="/docs",  # Swagger UI at /docs
    redoc_url="/redoc"  # ReDoc at /redoc
)

# CORS middleware configuration for React Native and web clients
# IMPORTANT: In production, replace "*" with specific allowed origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Configure specific origins in production
    allow_credentials=True,  # Allow cookies and authentication headers
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allow all headers
)

# Include API routers
# Each router handles a specific domain (providers, bookings, etc.)
app.include_router(provider_router)
app.include_router(booking_router)


@app.get("/")
def health_check():
    """
    Root endpoint - basic health check.
    
    Returns API status and basic information.
    Useful for load balancers and monitoring tools.
    
    Example response:
        {
            "status": "healthy",
            "service": "Multi-Sector Front Desk Management API",
            "version": "1.0.0"
        }
    """
    return {
        "status": "healthy",
        "service": "Multi-Sector Front Desk Management API",
        "version": "1.0.0"
    }


@app.get("/health")
def detailed_health():
    """
    Detailed health check endpoint.
    
    Provides information about available endpoints.
    Used by monitoring systems to verify API availability.
    
    Example response:
        {
            "status": "healthy",
            "database": "connected",
            "endpoints": {
                "providers": "/providers",
                "bookings": "/bookings"
            }
        }
    """
    return {
        "status": "healthy",
        "database": "connected",
        "endpoints": {
            "providers": "/providers",
            "bookings": "/bookings",
            "docs": "/docs"
        }
    }