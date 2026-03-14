"""LittleSearch FastAPI Application Entry Point."""

import logging
import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config.logging import setup_logging
from config.settings import get_settings
from presentation.api.v1 import documents, search, system

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
# Include routers
app.include_router(documents.router, prefix="/api/v1")
app.include_router(search.router, prefix="/api/v1")
app.include_router(system.router, prefix="/api/v1")


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
    return {"message": "Welcome to LittleSearch API", "docs": "/docs"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.API_RELOAD,
        log_level=settings.LOG_LEVEL.lower(),
    )
