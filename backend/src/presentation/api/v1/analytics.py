"""Analytics endpoints."""

import logging
from typing import Any

from fastapi import APIRouter, Depends, Query

from application.services.analytics_service import AnalyticsService
from presentation.dependencies import get_analytics_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/popular")
async def get_popular_queries(
    days: int = Query(7, ge=1, le=30, description="Days to look back"),
    top_n: int = Query(10, ge=1, le=50, description="Number of top queries"),
    analytics_service: AnalyticsService = Depends(get_analytics_service),
) -> dict[str, Any]:
    """Get most popular search queries.

    Args:
        days: Number of days to analyze
        top_n: Number of top queries to return
        analytics_service: Analytics service dependency

    Returns:
        dict: Popular queries with counts
    """
    popular = await analytics_service.get_popular_queries(days=days, top_n=top_n)
    return {"popular_queries": popular, "period_days": days}


@router.get("/stats")
async def get_search_stats(
    days: int = Query(7, ge=1, le=30, description="Days to look back"),
    analytics_service: AnalyticsService = Depends(get_analytics_service),
) -> dict[str, Any]:
    """Get search statistics.

    Args:
        days: Number of days to analyze
        analytics_service: Analytics service dependency

    Returns:
        dict: Search statistics
    """
    stats = await analytics_service.get_search_stats(days=days)
    return stats


@router.get("/trending")
async def get_trending_topics(
    hours: int = Query(24, ge=1, le=168, description="Hours to look back"),
    top_n: int = Query(10, ge=1, le=50, description="Number of trending topics"),
    analytics_service: AnalyticsService = Depends(get_analytics_service),
) -> dict[str, Any]:
    """Get trending search topics.

    Args:
        hours: Number of hours to analyze
        top_n: Number of topics to return
        analytics_service: Analytics service dependency

    Returns:
        dict: Trending topics
    """
    trending = await analytics_service.get_trending_topics(hours=hours, top_n=top_n)
    return {"trending_topics": trending, "period_hours": hours}
