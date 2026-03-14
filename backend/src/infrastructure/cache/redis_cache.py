"""Redis implementation for cache storage."""

import logging
from typing import Optional

import redis.asyncio as redis

from domain.interfaces import ICacheStore

logger = logging.getLogger(__name__)


class RedisCacheStore(ICacheStore):
    """Cache store implementation using Redis.

    This implementation provides a distributed cache for search results
    and other frequently accessed data.
    """

    def __init__(self, host: str, port: int, db: int = 0, password: Optional[str] = None):
        """Initialize Redis cache store.

        Args:
            host: Redis host
            port: Redis port
            db: Redis database number
            password: Optional Redis password
        """
        self._host = host
        self._port = port
        self._db = db
        self._password = password
        self._client: Optional[redis.Redis] = None
        logger.info(f"Initializing Redis cache: {host}:{port}/{db}")

    async def _ensure_connected(self) -> redis.Redis:
        """Ensure Redis connection is established.

        Returns:
            redis.Redis: Connected Redis client

        Raises:
            RuntimeError: If connection fails
        """
        if self._client is None:
            try:
                self._client = redis.Redis(
                    host=self._host,
                    port=self._port,
                    db=self._db,
                    password=self._password,
                    decode_responses=True,
                )
                # Test connection
                await self._client.ping()
                logger.info("Redis connection established")
            except Exception as e:
                logger.error(f"Failed to connect to Redis: {e}")
                raise RuntimeError(f"Redis connection failed: {e}") from e
        return self._client

    async def get(self, key: str) -> Optional[str]:
        """Retrieve value from cache.

        Args:
            key: Cache key

        Returns:
            Optional[str]: Cached value if found, None otherwise

        Raises:
            RuntimeError: If cache operation fails
        """
        try:
            client = await self._ensure_connected()
            value = await client.get(key)
            if value:
                logger.debug(f"Cache hit: {key}")
            else:
                logger.debug(f"Cache miss: {key}")
            return value
        except Exception as e:
            logger.error(f"Failed to get key {key}: {e}")
            raise RuntimeError(f"Cache get operation failed: {e}") from e

    async def set(self, key: str, value: str, ttl: int = 3600) -> bool:
        """Store value in cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (default: 1 hour)

        Returns:
            bool: True if successful

        Raises:
            ValueError: If key or value is empty
            RuntimeError: If cache operation fails
        """
        if not key:
            raise ValueError("Key cannot be empty")
        if not value:
            raise ValueError("Value cannot be empty")

        try:
            client = await self._ensure_connected()
            await client.setex(key, ttl, value)
            logger.debug(f"Cache set: {key} (TTL: {ttl}s)")
            return True
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Failed to set key {key}: {e}")
            raise RuntimeError(f"Cache set operation failed: {e}") from e

    async def delete(self, key: str) -> bool:
        """Delete value from cache.

        Args:
            key: Cache key

        Returns:
            bool: True if successful

        Raises:
            RuntimeError: If cache operation fails
        """
        try:
            client = await self._ensure_connected()
            result = await client.delete(key)
            logger.debug(f"Cache delete: {key}")
            return bool(result)
        except Exception as e:
            logger.error(f"Failed to delete key {key}: {e}")
            raise RuntimeError(f"Cache delete operation failed: {e}") from e

    async def exists(self, key: str) -> bool:
        """Check if key exists in cache.

        Args:
            key: Cache key

        Returns:
            bool: True if key exists

        Raises:
            RuntimeError: If cache operation fails
        """
        try:
            client = await self._ensure_connected()
            result = await client.exists(key)
            return bool(result)
        except Exception as e:
            logger.error(f"Failed to check existence of key {key}: {e}")
            raise RuntimeError(f"Cache exists operation failed: {e}") from e

    async def clear(self) -> bool:
        """Clear all cached values.

        Returns:
            bool: True if successful

        Raises:
            RuntimeError: If cache operation fails
        """
        try:
            client = await self._ensure_connected()
            await client.flushdb()
            logger.info("Cache cleared")
            return True
        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")
            raise RuntimeError(f"Cache clear operation failed: {e}") from e

    async def close(self) -> None:
        """Close Redis connection."""
        if self._client:
            await self._client.close()
            self._client = None
            logger.info("Redis connection closed")
