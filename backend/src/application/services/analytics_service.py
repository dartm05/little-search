"""Analytics service - track and analyze search patterns."""

import json
import logging
from collections import Counter
from datetime import datetime, timedelta
from typing import Any, Optional

from domain.interfaces import ICacheStore

logger = logging.getLogger(__name__)


class AnalyticsService:
    """Service for tracking search analytics and patterns."""

    def __init__(self, cache_store: ICacheStore):
        """Initialize analytics service.

        Args:
            cache_store: Cache store for persisting analytics
        """
        self._cache = cache_store
        self._analytics_prefix = "analytics:"
        logger.info("AnalyticsService initialized")

    async def record_search(
        self,
        query: str,
        results_count: int,
        execution_time_ms: float,
        filters: Optional[dict] = None,
    ) -> None:
        """Record a search query for analytics.

        Args:
            query: Search query
            results_count: Number of results returned
            execution_time_ms: Query execution time in milliseconds
            filters: Optional filters used
        """
        try:
            # Record in daily queries
            today = datetime.utcnow().strftime("%Y-%m-%d")
            queries_key = f"{self._analytics_prefix}queries:{today}"

            # Get existing queries
            existing = await self._cache.get(queries_key)
            queries_list = json.loads(existing) if existing else []

            # Add new query
            queries_list.append(
                {
                    "query": query,
                    "results_count": results_count,
                    "execution_time_ms": execution_time_ms,
                    "timestamp": datetime.utcnow().isoformat(),
                    "filters": filters,
                }
            )

            # Store back (keep last 1000 queries)
            if len(queries_list) > 1000:
                queries_list = queries_list[-1000:]

            await self._cache.set(
                queries_key, json.dumps(queries_list), ttl=86400 * 7  # 7 days
            )

            logger.debug(f"Recorded search: {query}")
        except Exception as e:
            logger.error(f"Failed to record search analytics: {e}")
            # Don't fail the search if analytics fails

    async def get_popular_queries(self, days: int = 7, top_n: int = 10) -> list[dict]:
        """Get most popular search queries.

        Args:
            days: Number of days to look back
            top_n: Number of top queries to return

        Returns:
            list[dict]: Popular queries with counts
        """
        try:
            all_queries = []

            # Collect queries from recent days
            for i in range(days):
                date = (datetime.utcnow() - timedelta(days=i)).strftime("%Y-%m-%d")
                queries_key = f"{self._analytics_prefix}queries:{date}"

                existing = await self._cache.get(queries_key)
                if existing:
                    day_queries = json.loads(existing)
                    all_queries.extend([q["query"].lower() for q in day_queries])

            # Count frequencies
            query_counts = Counter(all_queries)
            popular = [
                {"query": query, "count": count}
                for query, count in query_counts.most_common(top_n)
            ]

            return popular
        except Exception as e:
            logger.error(f"Failed to get popular queries: {e}")
            return []

    async def get_search_stats(self, days: int = 7) -> dict[str, Any]:
        """Get search statistics.

        Args:
            days: Number of days to look back

        Returns:
            dict: Search statistics
        """
        try:
            total_searches = 0
            total_results = 0
            total_execution_time = 0
            zero_result_queries = []

            # Collect stats from recent days
            for i in range(days):
                date = (datetime.utcnow() - timedelta(days=i)).strftime("%Y-%m-%d")
                queries_key = f"{self._analytics_prefix}queries:{date}"

                existing = await self._cache.get(queries_key)
                if existing:
                    day_queries = json.loads(existing)
                    total_searches += len(day_queries)

                    for q in day_queries:
                        total_results += q.get("results_count", 0)
                        total_execution_time += q.get("execution_time_ms", 0)

                        if q.get("results_count", 0) == 0:
                            zero_result_queries.append(q["query"])

            avg_results = total_results / total_searches if total_searches > 0 else 0
            avg_execution_time = (
                total_execution_time / total_searches if total_searches > 0 else 0
            )

            return {
                "period_days": days,
                "total_searches": total_searches,
                "average_results_per_search": round(avg_results, 2),
                "average_execution_time_ms": round(avg_execution_time, 2),
                "zero_result_queries_count": len(zero_result_queries),
                "zero_result_queries": list(set(zero_result_queries))[:10],
            }
        except Exception as e:
            logger.error(f"Failed to get search stats: {e}")
            return {}

    async def get_trending_topics(self, hours: int = 24, top_n: int = 10) -> list[str]:
        """Get trending search topics in recent hours.

        Args:
            hours: Number of hours to look back
            top_n: Number of trending topics to return

        Returns:
            list[str]: Trending topics
        """
        try:
            # For simplicity, using daily data
            # In production, would use hourly buckets
            today = datetime.utcnow().strftime("%Y-%m-%d")
            queries_key = f"{self._analytics_prefix}queries:{today}"

            existing = await self._cache.get(queries_key)
            if not existing:
                return []

            queries = json.loads(existing)

            # Filter to recent hours
            cutoff = datetime.utcnow() - timedelta(hours=hours)
            recent_queries = [
                q["query"]
                for q in queries
                if datetime.fromisoformat(q["timestamp"]) > cutoff
            ]

            # Extract keywords (simple word extraction)
            words = []
            for query in recent_queries:
                words.extend(query.lower().split())

            # Filter common words
            stopwords = {
                "the",
                "a",
                "an",
                "is",
                "in",
                "on",
                "at",
                "to",
                "for",
                "of",
                "and",
                "or",
            }
            filtered_words = [w for w in words if w not in stopwords and len(w) > 3]

            # Get most common
            word_counts = Counter(filtered_words)
            trending = [word for word, count in word_counts.most_common(top_n)]

            return trending
        except Exception as e:
            logger.error(f"Failed to get trending topics: {e}")
            return []
