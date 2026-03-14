"""Interface for vector database operations."""

from abc import ABC, abstractmethod
from typing import Optional

from domain.entities import Chunk


class IVectorStore(ABC):
    """Abstract interface for vector database operations.

    This interface defines the contract for vector store implementations.
    Implementations might use Qdrant, Weaviate, Pinecone, etc.
    """

    @abstractmethod
    async def upsert(self, chunks: list[Chunk]) -> bool:
        """Insert or update chunks in the vector store.

        Args:
            chunks: List of chunks with embeddings to upsert

        Returns:
            bool: True if successful

        Raises:
            ValueError: If chunks list is empty or chunks lack embeddings
            RuntimeError: If upsert operation fails
        """
        pass

    @abstractmethod
    async def search(
        self,
        query_embedding: list[float],
        top_k: int = 10,
        filter_conditions: Optional[dict] = None,
    ) -> list[tuple[Chunk, float]]:
        """Search for similar chunks by embedding.

        Args:
            query_embedding: Query vector embedding
            top_k: Number of results to return
            filter_conditions: Optional metadata filters

        Returns:
            list[tuple[Chunk, float]]: List of (chunk, similarity_score) tuples

        Raises:
            ValueError: If query_embedding is invalid or top_k < 1
            RuntimeError: If search operation fails
        """
        pass

    @abstractmethod
    async def delete_by_document_id(self, document_id: str) -> bool:
        """Delete all chunks belonging to a document.

        Args:
            document_id: ID of document whose chunks to delete

        Returns:
            bool: True if successful

        Raises:
            ValueError: If document_id is empty
            RuntimeError: If delete operation fails
        """
        pass

    @abstractmethod
    async def delete_by_chunk_id(self, chunk_id: str) -> bool:
        """Delete a specific chunk.

        Args:
            chunk_id: ID of chunk to delete

        Returns:
            bool: True if successful

        Raises:
            ValueError: If chunk_id is empty
            RuntimeError: If delete operation fails
        """
        pass

    @abstractmethod
    async def get_chunk_by_id(self, chunk_id: str) -> Optional[Chunk]:
        """Retrieve a chunk by its ID.

        Args:
            chunk_id: ID of chunk to retrieve

        Returns:
            Optional[Chunk]: Chunk if found, None otherwise

        Raises:
            RuntimeError: If retrieval operation fails
        """
        pass

    @abstractmethod
    async def count_chunks(self, document_id: Optional[str] = None) -> int:
        """Count chunks in the vector store.

        Args:
            document_id: Optional document ID to count chunks for

        Returns:
            int: Number of chunks

        Raises:
            RuntimeError: If count operation fails
        """
        pass
