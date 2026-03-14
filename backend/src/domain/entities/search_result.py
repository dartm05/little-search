"""SearchResult entity - represents a search result."""

from dataclasses import dataclass
from typing import Any

from .chunk import Chunk
from .document import Document


@dataclass
class SearchResult:
    """Domain entity representing a search result.

    Attributes:
        chunk: The matching chunk
        document: The parent document
        score: Similarity score (0.0 to 1.0)
    """

    chunk: Chunk
    document: Document
    score: float

    def __post_init__(self) -> None:
        """Validate search result after initialization."""
        if not isinstance(self.chunk, Chunk):
            raise TypeError("chunk must be a Chunk instance")
        if not isinstance(self.document, Document):
            raise TypeError("document must be a Document instance")
        if not isinstance(self.score, (int, float)):
            raise TypeError("score must be a number")
        if not 0.0 <= self.score <= 1.0:
            raise ValueError("score must be between 0.0 and 1.0")
        if self.chunk.document_id != self.document.id:
            raise ValueError("chunk document_id must match document id")

    def to_dict(self) -> dict[str, Any]:
        """Convert search result to dictionary representation.

        Returns:
            dict: Search result as dictionary
        """
        return {
            "chunk": self.chunk.to_dict(),
            "document": self.document.to_dict(),
            "score": self.score,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SearchResult":
        """Create search result from dictionary.

        Args:
            data: Dictionary containing search result data

        Returns:
            SearchResult: New search result instance
        """
        return cls(
            chunk=Chunk.from_dict(data["chunk"]),
            document=Document.from_dict(data["document"]),
            score=data["score"],
        )
