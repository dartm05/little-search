"""Qdrant implementation for vector storage."""

import logging
import uuid
from typing import Optional

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    MatchValue,
    PointStruct,
    VectorParams,
)

from domain.entities import Chunk
from domain.interfaces import IVectorStore

logger = logging.getLogger(__name__)


class QdrantVectorStore(IVectorStore):
    """Vector store implementation using Qdrant.

    This implementation provides semantic search capabilities using
    Qdrant's vector similarity search.
    """

    def __init__(
        self,
        host: str,
        port: int,
        collection_name: str,
        vector_size: int,
    ):
        """Initialize Qdrant vector store.

        Args:
            host: Qdrant host
            port: Qdrant port
            collection_name: Name of the collection to use
            vector_size: Dimension of vector embeddings
        """
        self._host = host
        self._port = port
        self._collection_name = collection_name
        self._vector_size = vector_size
        self._client: Optional[QdrantClient] = None
        logger.info(f"Initializing Qdrant: {host}:{port}, collection: {collection_name}")

    def _ensure_connected(self) -> QdrantClient:
        """Ensure Qdrant client is initialized.

        Returns:
            QdrantClient: Connected Qdrant client

        Raises:
            RuntimeError: If connection or collection creation fails
        """
        if self._client is None:
            try:
                self._client = QdrantClient(host=self._host, port=self._port)
                self._ensure_collection_exists()
                logger.info("Qdrant client initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Qdrant client: {e}")
                raise RuntimeError(f"Qdrant initialization failed: {e}") from e
        return self._client

    def _ensure_collection_exists(self) -> None:
        """Create collection if it doesn't exist.

        Raises:
            RuntimeError: If collection creation fails
        """
        try:
            collections = self._client.get_collections().collections
            collection_names = [c.name for c in collections]

            if self._collection_name not in collection_names:
                self._client.create_collection(
                    collection_name=self._collection_name,
                    vectors_config=VectorParams(
                        size=self._vector_size, distance=Distance.COSINE
                    ),
                )
                logger.info(f"Created collection: {self._collection_name}")
            else:
                logger.debug(f"Collection already exists: {self._collection_name}")
        except Exception as e:
            logger.error(f"Failed to ensure collection exists: {e}")
            raise RuntimeError(f"Collection creation failed: {e}") from e

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
        if not chunks:
            raise ValueError("Chunks list cannot be empty")

        # Validate all chunks have embeddings
        for chunk in chunks:
            if not chunk.has_embedding:
                raise ValueError(f"Chunk {chunk.id} missing embedding")

        try:
            client = self._ensure_connected()

            points = [
                PointStruct(
                    id=str(uuid.uuid5(uuid.NAMESPACE_DNS, chunk.id)),
                    vector=chunk.embedding,
                    payload={
                        "chunk_id": chunk.id, 
                        "document_id": chunk.document_id,
                        "content": chunk.content,
                        "chunk_index": chunk.chunk_index,
                        "metadata": chunk.metadata,
                    },
                )
                for chunk in chunks
            ]

            client.upsert(collection_name=self._collection_name, points=points)
            logger.info(f"Upserted {len(chunks)} chunks")
            return True
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Failed to upsert chunks: {e}")
            raise RuntimeError(f"Upsert operation failed: {e}") from e

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
        if not query_embedding:
            raise ValueError("Query embedding cannot be empty")
        if top_k < 1:
            raise ValueError("top_k must be at least 1")

        try:
            client = self._ensure_connected()

            # Build filter if provided
            query_filter = None
            if filter_conditions:
                query_filter = Filter(
                    must=[
                        FieldCondition(
                            key=key, match=MatchValue(value=value)
                        )
                        for key, value in filter_conditions.items()
                    ]
                )

            results = client.search(
                collection_name=self._collection_name,
                query_vector=query_embedding,
                limit=top_k,
                query_filter=query_filter,
            )

            # Convert results to chunks
            search_results = []
            for result in results:
                chunk = Chunk(
                    id=result.payload.get("chunk_id", str(result.id)),
                    document_id=result.payload["document_id"],
                    content=result.payload["content"],
                    chunk_index=result.payload["chunk_index"],
                    embedding=result.vector if hasattr(result, "vector") else None,
                    metadata=result.payload.get("metadata", {}),
                )
                search_results.append((chunk, result.score))

            logger.info(f"Search returned {len(search_results)} results")
            return search_results
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Failed to search: {e}")
            raise RuntimeError(f"Search operation failed: {e}") from e

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
        if not document_id:
            raise ValueError("Document ID cannot be empty")

        try:
            client = self._ensure_connected()

            client.delete(
                collection_name=self._collection_name,
                points_selector=Filter(
                    must=[
                        FieldCondition(
                            key="document_id", match=MatchValue(value=document_id)
                        )
                    ]
                ),
            )
            logger.info(f"Deleted chunks for document: {document_id}")
            return True
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Failed to delete chunks for document {document_id}: {e}")
            raise RuntimeError(f"Delete operation failed: {e}") from e

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
        if not chunk_id:
            raise ValueError("Chunk ID cannot be empty")

        try:
            client = self._ensure_connected()
            client.delete(
                collection_name=self._collection_name, points_selector=[chunk_id]
            )
            logger.info(f"Deleted chunk: {chunk_id}")
            return True
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Failed to delete chunk {chunk_id}: {e}")
            raise RuntimeError(f"Delete operation failed: {e}") from e

    async def get_chunk_by_id(self, chunk_id: str) -> Optional[Chunk]:
        """Retrieve a chunk by its ID.

        Args:
            chunk_id: ID of chunk to retrieve

        Returns:
            Optional[Chunk]: Chunk if found, None otherwise

        Raises:
            RuntimeError: If retrieval operation fails
        """
        try:
            client = self._ensure_connected()
            result = client.retrieve(
                collection_name=self._collection_name, ids=[chunk_id]
            )

            if not result:
                return None

            point = result[0]
            chunk = Chunk(
                id=str(point.id),
                document_id=point.payload["document_id"],
                content=point.payload["content"],
                chunk_index=point.payload["chunk_index"],
                embedding=point.vector if hasattr(point, "vector") else None,
                metadata=point.payload.get("metadata", {}),
            )
            return chunk
        except Exception as e:
            logger.error(f"Failed to retrieve chunk {chunk_id}: {e}")
            raise RuntimeError(f"Retrieval operation failed: {e}") from e

    async def count_chunks(self, document_id: Optional[str] = None) -> int:
        """Count chunks in the vector store.

        Args:
            document_id: Optional document ID to count chunks for

        Returns:
            int: Number of chunks

        Raises:
            RuntimeError: If count operation fails
        """
        try:
            client = self._ensure_connected()

            if document_id:
                result = client.count(
                    collection_name=self._collection_name,
                    count_filter=Filter(
                        must=[
                            FieldCondition(
                                key="document_id", match=MatchValue(value=document_id)
                            )
                        ]
                    ),
                )
            else:
                result = client.count(collection_name=self._collection_name)

            return result.count
        except Exception as e:
            logger.error(f"Failed to count chunks: {e}")
            raise RuntimeError(f"Count operation failed: {e}") from e
