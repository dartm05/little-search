"""Document entity - represents a document in the system."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class Document:
    """Domain entity representing a document to be indexed.

    Attributes:
        id: Unique identifier for the document
        content: Full text content of the document
        metadata: Additional document metadata (author, title, etc.)
        created_at: Timestamp when document was created
    """

    id: str
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self) -> None:
        """Validate document after initialization."""
        if not self.id:
            raise ValueError("Document ID cannot be empty")
        if not self.content:
            raise ValueError("Document content cannot be empty")
        if not isinstance(self.metadata, dict):
            raise TypeError("Document metadata must be a dictionary")

    @property
    def content_length(self) -> int:
        """Get the length of document content.

        Returns:
            int: Number of characters in content
        """
        return len(self.content)

    def to_dict(self) -> dict[str, Any]:
        """Convert document to dictionary representation.

        Returns:
            dict: Document as dictionary
        """
        return {
            "id": self.id,
            "content": self.content,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Document":
        """Create document from dictionary.

        Args:
            data: Dictionary containing document data

        Returns:
            Document: New document instance
        """
        created_at = data.get("created_at")
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        elif created_at is None:
            created_at = datetime.utcnow()

        return cls(
            id=data["id"],
            content=data["content"],
            metadata=data.get("metadata", {}),
            created_at=created_at,
        )
