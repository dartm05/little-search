"""Interface for document chunking."""

from abc import ABC, abstractmethod

from domain.entities import Chunk, Document


class IChunker(ABC):
    """Abstract interface for document chunking strategies.

    This interface defines the contract for chunking implementations.
    Different strategies might use fixed-size, semantic, or sentence-based chunking.
    """

    @abstractmethod
    def chunk(self, document: Document) -> list[Chunk]:
        """Split a document into chunks.

        Args:
            document: Document to chunk

        Returns:
            list[Chunk]: List of document chunks

        Raises:
            ValueError: If document is invalid
            RuntimeError: If chunking fails
        """
        pass

    @abstractmethod
    def get_chunk_size(self) -> int:
        """Get the target chunk size in characters.

        Returns:
            int: Target chunk size
        """
        pass

    @abstractmethod
    def get_chunk_overlap(self) -> int:
        """Get the overlap size between chunks in characters.

        Returns:
            int: Chunk overlap size
        """
        pass
