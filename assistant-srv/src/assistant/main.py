"""
FastAPI application configuration and setup.
"""

from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.auth import router as auth_router
from .api.oauth import router as oauth_router
from .api.sessions import router as sessions_router
from .api.users import router as users_router
from .models.api.general_api import HealthCheckResponseData, StatusResponseData


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
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
    lifespan=lifespan,
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
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(oauth_router)
app.include_router(sessions_router)


@app.get("/", response_model=StatusResponseData)  # type: ignore[misc]
async def root() -> StatusResponseData:
    """Root endpoint."""
    return StatusResponseData(
        status="running",
        data={
            "message": "Personal AI Assistant Server",
            "version": "0.1.0",
        },
    )


@app.get("/health", response_model=HealthCheckResponseData)  # type: ignore[misc]
async def health_check() -> HealthCheckResponseData:
    """Health check endpoint."""
    return HealthCheckResponseData(status="healthy", timestamp=datetime.now(timezone.utc).isoformat())


if __name__ == "__main__":
    import uvicorn

    from .core.config import config

    uvicorn.run("assistant.main:app", host=config.host, port=config.port, reload=config.debug)
