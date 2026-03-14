"""Search service - orchestrates search operations."""

import hashlib
import json
import logging
from typing import Optional

from domain.entities import Document, SearchResult
from domain.interfaces import (
    ICacheStore,
    IEmbeddingGenerator,
    ILLMProvider,
    IVectorStore,
)

logger = logging.getLogger(__name__)


class SearchService:
    """Service for orchestrating semantic search operations.

    This service follows the Single Responsibility Principle by focusing
    solely on search orchestration, delegating specific tasks to injected
    dependencies.
    """

    def __init__(
        self,
        embedding_generator: IEmbeddingGenerator,
        vector_store: IVectorStore,
        cache_store: ICacheStore,
        llm_provider: Optional[ILLMProvider] = None,
        cache_ttl: int = 3600,
    ):
        """Initialize search service.

        Args:
            embedding_generator: Service for generating embeddings
            vector_store: Vector database for similarity search
            cache_store: Cache for storing frequent queries
            llm_provider: Optional LLM for result summarization
            cache_ttl: Cache time-to-live in seconds
        """
        self._embedding_generator = embedding_generator
        self._vector_store = vector_store
        self._cache_store = cache_store
        self._llm_provider = llm_provider
        self._cache_ttl = cache_ttl
        logger.info("SearchService initialized")

    def _generate_cache_key(self, query: str, top_k: int, filters: Optional[dict] = None) -> str:
        """Generate a cache key for a search query.

        Args:
            query: Search query
            top_k: Number of results
            filters: Optional filters

        Returns:
            str: Cache key
        """
        key_data = {"query": query, "top_k": top_k, "filters": filters or {}}
        key_str = json.dumps(key_data, sort_keys=True)
        return f"search:{hashlib.md5(key_str.encode()).hexdigest()}"

    async def search(
        self,
        query: str,
        top_k: int = 10,
        filter_conditions: Optional[dict] = None,
        use_cache: bool = True,
    ) -> list[SearchResult]:
        """Perform semantic search.

        Args:
            query: Search query text
            top_k: Number of results to return
            filter_conditions: Optional metadata filters
            use_cache: Whether to use cache

        Returns:
            list[SearchResult]: Search results with scores

        Raises:
            ValueError: If query is empty or top_k is invalid
            RuntimeError: If search operation fails
        """
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")
        if top_k < 1:
            raise ValueError("top_k must be at least 1")

        logger.info(f"Searching for: '{query}' (top_k={top_k})")

        # Check cache
        cache_key = self._generate_cache_key(query, top_k, filter_conditions)
        if use_cache:
            cached_result = await self._cache_store.get(cache_key)
            if cached_result:
                logger.info("Returning cached search results")
                # In production, would deserialize full SearchResult objects
                # For now, just note cache hit
                # return self._deserialize_results(cached_result)

        try:
            # Generate query embedding
            logger.debug("Generating query embedding")
            query_embedding = await self._embedding_generator.generate_embedding(query)

            # Search vector store
            logger.debug("Searching vector store")
            results = await self._vector_store.search(
                query_embedding=query_embedding,
                top_k=top_k,
                filter_conditions=filter_conditions,
            )

            # Convert to SearchResult entities
            # Note: In production, we'd need to fetch full Document objects
            # For now, creating minimal Document objects from chunk metadata
            search_results = []
            for chunk, score in results:
                # Create a minimal document representation
                # In production, this would fetch from a document store
                document = Document(
                    id=chunk.document_id,
                    content=chunk.content,  # Simplified - would fetch full content
                    metadata=chunk.metadata,
                )
                search_result = SearchResult(
                    chunk=chunk, document=document, score=score
                )
                search_results.append(search_result)

            logger.info(f"Found {len(search_results)} results")

            # Cache results
            if use_cache and search_results:
                # Simplified caching - in production would serialize properly
                cache_value = json.dumps(
                    [
                        {
                            "chunk_id": sr.chunk.id,
                            "document_id": sr.document.id,
                            "score": sr.score,
                        }
                        for sr in search_results
                    ]
                )
                await self._cache_store.set(cache_key, cache_value, self._cache_ttl)

            return search_results

        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Search failed: {e}")
            raise RuntimeError(f"Search operation failed: {e}") from e

    async def search_with_summary(
        self, query: str, top_k: int = 10, max_summary_tokens: int = 500
    ) -> tuple[list[SearchResult], Optional[str]]:
        """Perform search and generate a summary of results.

        Args:
            query: Search query
            top_k: Number of results
            max_summary_tokens: Max tokens for summary

        Returns:
            tuple: (search_results, summary_text)

        Raises:
            ValueError: If query is invalid
            RuntimeError: If operation fails
        """
        # Perform search
        results = await self.search(query, top_k, use_cache=True)

        # Generate summary if LLM is available
        summary = None
        if self._llm_provider and self._llm_provider.is_available() and results:
            try:
                # Combine top results as context
                context = "\n\n".join(
                    [f"[{i+1}] {sr.chunk.content}" for i, sr in enumerate(results[:5])]
                )
                summary = await self._llm_provider.summarize(context, query)
                logger.info("Generated summary for search results")
            except Exception as e:
                logger.warning(f"Failed to generate summary: {e}")
                # Continue without summary

        return results, summary
