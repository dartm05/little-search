"""LittleSearch FastAPI Application Entry Point."""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config.logging import setup_logging
from config.settings import get_settings

# Set up logging
setup_logging()
logger = logging.getLogger(__name__)

# Get settings
settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title="LittleSearch",
    description="Distributed Semantic Search Engine",
    version="0.1.0",
    debug=settings.DEBUG,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event() -> None:
    """Handle application startup."""
    logger.info(f"Starting LittleSearch in {settings.ENVIRONMENT} mode")
    logger.info(f"API running on {settings.API_HOST}:{settings.API_PORT}")


@app.on_event("shutdown")
async def shutdown_event() -> None:
    """Handle application shutdown."""
    logger.info("Shutting down LittleSearch")


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint.

    Returns:
        dict: Welcome message
    """
    return {"message": "Welcome to LittleSearch API"}


@app.get("/api/v1/health")
async def health() -> dict[str, str]:
    """Health check endpoint.

    Returns:
        dict: Health status
    """
    return {"status": "healthy", "version": "0.1.0"}


@app.get("/api/v1/ready")
async def ready() -> dict[str, bool]:
    """Readiness probe endpoint.

    Returns:
        dict: Readiness status
    """
    # TODO: Add actual checks for Redis, Qdrant, etc.
    return {"ready": True}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.API_RELOAD,
        log_level=settings.LOG_LEVEL.lower(),
    )
