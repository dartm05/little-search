"""System health and status endpoints."""

import logging
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, status

from config.settings import get_settings
from infrastructure.cache import RedisCacheStore
from infrastructure.database import QdrantVectorStore
from presentation.api.models import HealthResponse
from presentation.dependencies import get_cache_store, get_vector_store

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/system", tags=["system"])


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Basic health check endpoint.

    Returns:
        HealthResponse: Health status
    """
    return HealthResponse(status="healthy", version="0.1.0", timestamp=datetime.utcnow())


@router.get("/ready")
async def readiness_check(
    cache_store: RedisCacheStore = Depends(get_cache_store),
    vector_store: QdrantVectorStore = Depends(get_vector_store),
) -> dict[str, Any]:
    """Readiness probe that checks dependencies.

    Args:
        cache_store: Cache store dependency
        vector_store: Vector store dependency

    Returns:
        dict: Readiness status with component checks
    """
    checks = {"ready": True, "components": {}}

    # Check Redis
    try:
        await cache_store.exists("health_check")
        checks["components"]["redis"] = "healthy"
    except Exception as e:
        logger.warning(f"Redis health check failed: {e}")
        checks["components"]["redis"] = "unhealthy"
        checks["ready"] = False

    # Check Qdrant
    try:
        await vector_store.count_chunks()
        checks["components"]["qdrant"] = "healthy"
    except Exception as e:
        logger.warning(f"Qdrant health check failed: {e}")
        checks["components"]["qdrant"] = "unhealthy"
        checks["ready"] = False

    return checks


@router.get("/stats")
async def get_system_stats(
    vector_store: QdrantVectorStore = Depends(get_vector_store),
) -> dict[str, Any]:
    """Get system statistics.

    Args:
        vector_store: Vector store dependency

    Returns:
        dict: System statistics
    """
    try:
        total_chunks = await vector_store.count_chunks()

        return {
            "total_chunks": total_chunks,
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Failed to get stats: {e}")
        return {"error": str(e), "timestamp": datetime.utcnow().isoformat()}
