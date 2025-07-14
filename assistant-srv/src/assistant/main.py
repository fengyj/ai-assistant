"""
Main FastAPI application.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .core import config
from .api.users import router as users_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    print("Starting Personal AI Assistant Server...")
    yield
    # Shutdown
    print("Shutting down Personal AI Assistant Server...")


# Create FastAPI app
app = FastAPI(
    title="Personal AI Assistant Server",
    description="A comprehensive AI assistant backend server",
    version="0.1.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(users_router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Personal AI Assistant Server",
        "version": "0.1.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": "2025-01-11T00:00:00Z"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "assistant.main:app",
        host=config.host,
        port=config.port,
        reload=config.debug
    )
