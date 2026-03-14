"""Sliding window chunker implementation."""

import logging
import uuid

from domain.entities import Chunk, Document
from domain.interfaces import IChunker

logger = logging.getLogger(__name__)


class SlidingWindowChunker(IChunker):
    """Chunker using sliding window with overlap.

    This implementation splits documents into fixed-size chunks with
    configurable overlap to maintain context between chunks.
    """

    def __init__(self, chunk_size: int = 512, chunk_overlap: int = 50):
        """Initialize sliding window chunker.

        Args:
            chunk_size: Target size of each chunk in characters
            chunk_overlap: Number of overlapping characters between chunks
        """
        if chunk_size <= 0:
            raise ValueError("Chunk size must be positive")
        if chunk_overlap < 0:
            raise ValueError("Chunk overlap must be non-negative")
        if chunk_overlap >= chunk_size:
            raise ValueError("Chunk overlap must be less than chunk size")

        self._chunk_size = chunk_size
        self._chunk_overlap = chunk_overlap
        logger.info(
            f"Initialized SlidingWindowChunker: size={chunk_size}, overlap={chunk_overlap}"
        )

    def chunk(self, document: Document) -> list[Chunk]:
        """Split a document into chunks using sliding window.

        Args:
            document: Document to chunk

        Returns:
            list[Chunk]: List of document chunks

        Raises:
            ValueError: If document is invalid
            RuntimeError: If chunking fails
        """
        if not document.content:
            raise ValueError("Document content cannot be empty")

        try:
            chunks = []
            content = document.content
            step = self._chunk_size - self._chunk_overlap
            chunk_index = 0

            for start in range(0, len(content), step):
                end = min(start + self._chunk_size, len(content))
                chunk_content = content[start:end]

                # Skip very small final chunks
                if len(chunk_content.strip()) < 10 and chunks:
                    # Merge with last chunk if it's tiny
                    last_chunk = chunks[-1]
                    chunks[-1] = Chunk(
                        id=last_chunk.id,
                        document_id=last_chunk.document_id,
                        content=last_chunk.content + " " + chunk_content,
                        chunk_index=last_chunk.chunk_index,
                        metadata=last_chunk.metadata,
                    )
                    break

                chunk = Chunk(
                    id=f"{document.id}_chunk_{chunk_index}",
                    document_id=document.id,
                    content=chunk_content.strip(),
                    chunk_index=chunk_index,
                    metadata={
                        **document.metadata,
                        "start_char": start,
                        "end_char": end,
                    },
                )
                chunks.append(chunk)
                chunk_index += 1

                # Break if we've reached the end
                if end >= len(content):
                    break

            logger.debug(
                f"Chunked document {document.id} into {len(chunks)} chunks"
            )
            return chunks
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Failed to chunk document {document.id}: {e}")
            raise RuntimeError(f"Chunking failed: {e}") from e

    def get_chunk_size(self) -> int:
        """Get the target chunk size in characters.

        Returns:
            int: Target chunk size
        """
        return self._chunk_size

    def get_chunk_overlap(self) -> int:
        """Get the overlap size between chunks in characters.

        Returns:
            int: Chunk overlap size
        """
        return self._chunk_overlap
