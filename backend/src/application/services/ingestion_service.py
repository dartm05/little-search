"""Ingestion service - orchestrates document ingestion."""

import logging
from typing import Any, Optional

from domain.entities import Document
from domain.interfaces import IChunker, IEmbeddingGenerator, IVectorStore

logger = logging.getLogger(__name__)


class IngestionService:
    """Service for orchestrating document ingestion.

    This service follows the Single Responsibility Principle by focusing
    solely on ingestion orchestration, delegating specific tasks to injected
    dependencies.
    """

    def __init__(
        self,
        chunker: IChunker,
        embedding_generator: IEmbeddingGenerator,
        vector_store: IVectorStore,
    ):
        """Initialize ingestion service.

        Args:
            chunker: Service for chunking documents
            embedding_generator: Service for generating embeddings
            vector_store: Vector database for storing chunks
        """
        self._chunker = chunker
        self._embedding_generator = embedding_generator
        self._vector_store = vector_store
        logger.info("IngestionService initialized")

    async def ingest_document(self, document: Document) -> dict[str, Any]:
        """Ingest a document into the search system.

        This orchestrates the full pipeline:
        1. Chunk the document
        2. Generate embeddings for chunks
        3. Store chunks in vector database

        Args:
            document: Document to ingest

        Returns:
            dict: Ingestion results with statistics

        Raises:
            ValueError: If document is invalid
            RuntimeError: If ingestion fails
        """
        if not document.content:
            raise ValueError("Document content cannot be empty")

        logger.info(f"Starting ingestion for document: {document.id}")

        try:
            # Step 1: Chunk the document
            logger.debug(f"Chunking document {document.id}")
            chunks = self._chunker.chunk(document)
            logger.info(f"Created {len(chunks)} chunks from document {document.id}")

            if not chunks:
                raise ValueError("No chunks generated from document")

            # Step 2: Generate embeddings for all chunks
            logger.debug(f"Generating embeddings for {len(chunks)} chunks")
            chunk_texts = [chunk.content for chunk in chunks]
            embeddings = await self._embedding_generator.generate_embeddings_batch(
                chunk_texts
            )

            # Attach embeddings to chunks
            for chunk, embedding in zip(chunks, embeddings):
                chunk.set_embedding(embedding)

            logger.info(f"Generated embeddings for {len(chunks)} chunks")

            # Step 3: Store chunks in vector database
            logger.debug(f"Storing {len(chunks)} chunks in vector store")
            success = await self._vector_store.upsert(chunks)

            if not success:
                raise RuntimeError("Failed to store chunks in vector database")

            logger.info(f"Successfully ingested document {document.id}")

            return {
                "document_id": document.id,
                "chunks_created": len(chunks),
                "status": "success",
                "chunk_ids": [chunk.id for chunk in chunks],
            }

        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Failed to ingest document {document.id}: {e}")
            raise RuntimeError(f"Document ingestion failed: {e}") from e

    async def delete_document(self, document_id: str) -> bool:
        """Delete a document and all its chunks.

        Args:
            document_id: ID of document to delete

        Returns:
            bool: True if successful

        Raises:
            ValueError: If document_id is empty
            RuntimeError: If deletion fails
        """
        if not document_id:
            raise ValueError("Document ID cannot be empty")

        logger.info(f"Deleting document: {document_id}")

        try:
            # Delete all chunks for this document
            success = await self._vector_store.delete_by_document_id(document_id)

            if success:
                logger.info(f"Successfully deleted document {document_id}")
            else:
                logger.warning(f"Failed to delete document {document_id}")

            return success

        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Failed to delete document {document_id}: {e}")
            raise RuntimeError(f"Document deletion failed: {e}") from e

    async def get_document_stats(self, document_id: str) -> dict[str, Any]:
        """Get statistics for a document.

        Args:
            document_id: ID of document

        Returns:
            dict: Document statistics

        Raises:
            RuntimeError: If operation fails
        """
        try:
            chunk_count = await self._vector_store.count_chunks(document_id)

            return {
                "document_id": document_id,
                "chunk_count": chunk_count,
                "exists": chunk_count > 0,
            }

        except Exception as e:
            logger.error(f"Failed to get stats for document {document_id}: {e}")
            raise RuntimeError(f"Failed to get document stats: {e}") from e

    async def reindex_document(
        self, document: Document, delete_old: bool = True
    ) -> dict[str, Any]:
        """Reindex an existing document.

        Args:
            document: Document to reindex
            delete_old: Whether to delete old chunks first

        Returns:
            dict: Reindexing results

        Raises:
            ValueError: If document is invalid
            RuntimeError: If reindexing fails
        """
        logger.info(f"Reindexing document: {document.id}")

        try:
            # Delete old chunks if requested
            if delete_old:
                await self.delete_document(document.id)

            # Ingest the document
            result = await self.ingest_document(document)
            result["reindexed"] = True

            return result

        except Exception as e:
            logger.error(f"Failed to reindex document {document.id}: {e}")
            raise RuntimeError(f"Document reindexing failed: {e}") from e
