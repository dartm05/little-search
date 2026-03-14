"""Chunk entity - represents a document chunk."""

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class Chunk:
    """Domain entity representing a chunk of a document.

    Attributes:
        id: Unique identifier for the chunk
        document_id: ID of the parent document
        content: Text content of the chunk
        embedding: Vector embedding for semantic search (None until generated)
        chunk_index: Position of this chunk within the document
        metadata: Additional chunk metadata
    """

    id: str
    document_id: str
    content: str
    chunk_index: int
    embedding: Optional[list[float]] = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate chunk after initialization."""
        if not self.id:
            raise ValueError("Chunk ID cannot be empty")
        if not self.document_id:
            raise ValueError("Chunk document_id cannot be empty")
        if not self.content:
            raise ValueError("Chunk content cannot be empty")
        if self.chunk_index < 0:
            raise ValueError("Chunk index must be non-negative")
        if self.embedding is not None and not isinstance(self.embedding, list):
            raise TypeError("Chunk embedding must be a list or None")

    @property
    def has_embedding(self) -> bool:
        """Check if chunk has an embedding.

        Returns:
            bool: True if embedding is present
        """
        return self.embedding is not None and len(self.embedding) > 0

    @property
    def content_length(self) -> int:
        """Get the length of chunk content.

        Returns:
            int: Number of characters in content
        """
        return len(self.content)

    def set_embedding(self, embedding: list[float]) -> None:
        """Set the embedding for this chunk.

        Args:
            embedding: Vector embedding
        """
        if not isinstance(embedding, list):
            raise TypeError("Embedding must be a list")
        if not embedding:
            raise ValueError("Embedding cannot be empty")
        self.embedding = embedding

    def to_dict(self) -> dict[str, Any]:
        """Convert chunk to dictionary representation.

        Returns:
            dict: Chunk as dictionary
        """
        return {
            "id": self.id,
            "document_id": self.document_id,
            "content": self.content,
            "chunk_index": self.chunk_index,
            "embedding": self.embedding,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Chunk":
        """Create chunk from dictionary.

        Args:
            data: Dictionary containing chunk data

        Returns:
            Chunk: New chunk instance
        """
        return cls(
            id=data["id"],
            document_id=data["document_id"],
            content=data["content"],
            chunk_index=data["chunk_index"],
            embedding=data.get("embedding"),
            metadata=data.get("metadata", {}),
        )
