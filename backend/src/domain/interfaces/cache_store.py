"""Interface for cache operations."""

from abc import ABC, abstractmethod
from typing import Optional


class ICacheStore(ABC):
    """Abstract interface for cache storage operations.

    This interface defines the contract for cache implementations.
    Implementations might use Redis, Memcached, in-memory cache, etc.
    """

    @abstractmethod
    async def get(self, key: str) -> Optional[str]:
        """Retrieve value from cache.

        Args:
            key: Cache key

        Returns:
            Optional[str]: Cached value if found, None otherwise

        Raises:
            RuntimeError: If cache operation fails
        """
        pass

    @abstractmethod
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
        pass

    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Delete value from cache.

        Args:
            key: Cache key

        Returns:
            bool: True if successful

        Raises:
            RuntimeError: If cache operation fails
        """
        pass

    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache.

        Args:
            key: Cache key

        Returns:
            bool: True if key exists

        Raises:
            RuntimeError: If cache operation fails
        """
        pass

    @abstractmethod
    async def clear(self) -> bool:
        """Clear all cached values.

        Returns:
            bool: True if successful

        Raises:
            RuntimeError: If cache operation fails
        """
        pass
