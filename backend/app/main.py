"""
FastAPI application entry point for LeadFlow.

This module creates the FastAPI application, configures CORS,
registers routers, and sets up startup hooks.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, Base
from app.routers import leads, discussions

# Create FastAPI application
app = FastAPI(
    title="LeadFlow API",
    description="Lead Management API for tracking sales prospects and discussions",
    version="1.0.0"
)

# Configure CORS
# Allow all origins for development. In production, restrict to frontend domain.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (development only)
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Register routers
app.include_router(leads.router)
app.include_router(discussions.router)


@app.on_event("startup")
def startup_event():
    """
    Run on application startup.

    Creates all database tables if they don't exist.
    No migration tool needed for this scale.
    """
    Base.metadata.create_all(bind=engine)


@app.get("/health")
def health_check():
    """
    Health check endpoint.

    Simple endpoint to verify the server is running.
    Useful for load balancers, uptime monitors, and quick verification.

    Returns:
        dict: Status message
    """
    return {"status": "ok"}


@app.get("/")
def root():
    """
    Root endpoint.

    Redirects users to API documentation.

    Returns:
        dict: Welcome message with links
    """
    return {
        "message": "LeadFlow API",
        "docs": "/docs",
        "health": "/health"
    }
