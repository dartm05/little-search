"""Dependency injection for FastAPI."""

from functools import lru_cache

from application.services import IngestionService, SearchService
from config.settings import get_settings
from infrastructure.cache import RedisCacheStore
from infrastructure.chunking import SlidingWindowChunker
from infrastructure.database import QdrantVectorStore
from infrastructure.embeddings import SentenceTransformerEmbeddings


@lru_cache()
def get_embedding_generator() -> SentenceTransformerEmbeddings:
    """Get embedding generator instance.

    Returns:
        SentenceTransformerEmbeddings: Embedding generator
    """
    settings = get_settings()
    return SentenceTransformerEmbeddings(
        model_name=settings.EMBEDDING_MODEL, dimension=settings.EMBEDDING_DIMENSION
    )


@lru_cache()
def get_vector_store() -> QdrantVectorStore:
    """Get vector store instance.

    Returns:
        QdrantVectorStore: Vector store
    """
    settings = get_settings()
    return QdrantVectorStore(
        host=settings.QDRANT_HOST,
        port=settings.QDRANT_PORT,
        collection_name=settings.COLLECTION_NAME,
        vector_size=settings.VECTOR_SIZE,
    )


@lru_cache()
def get_cache_store() -> RedisCacheStore:
    """Get cache store instance.

    Returns:
        RedisCacheStore: Cache store
    """
    settings = get_settings()
    return RedisCacheStore(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=settings.REDIS_DB,
        password=settings.REDIS_PASSWORD,
    )


@lru_cache()
def get_chunker() -> SlidingWindowChunker:
    """Get chunker instance.

    Returns:
        SlidingWindowChunker: Chunker
    """
    settings = get_settings()
    return SlidingWindowChunker(
        chunk_size=settings.CHUNK_SIZE, chunk_overlap=settings.CHUNK_OVERLAP
    )


@lru_cache()
def get_search_service() -> SearchService:
    """Get search service instance.

    Returns:
        SearchService: Search service
    """
    settings = get_settings()
    return SearchService(
        embedding_generator=get_embedding_generator(),
        vector_store=get_vector_store(),
        cache_store=get_cache_store(),
        llm_provider=None,  # Optional: add LLM provider
        cache_ttl=settings.CACHE_TTL_SECONDS,
    )


@lru_cache()
def get_ingestion_service() -> IngestionService:
    """Get ingestion service instance.

    Returns:
        IngestionService: Ingestion service
    """
    return IngestionService(
        chunker=get_chunker(),
        embedding_generator=get_embedding_generator(),
        vector_store=get_vector_store(),
    )
