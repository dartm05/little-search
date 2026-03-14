"""Interface for embedding generation."""

from abc import ABC, abstractmethod


class IEmbeddingGenerator(ABC):
    """Abstract interface for generating text embeddings.

    This interface defines the contract for embedding generation implementations.
    Implementations might use sentence-transformers, OpenAI, etc.
    """

    @abstractmethod
    async def generate_embedding(self, text: str) -> list[float]:
        """Generate embedding for a single text.

        Args:
            text: Input text to embed

        Returns:
            list[float]: Vector embedding

        Raises:
            ValueError: If text is empty
            RuntimeError: If embedding generation fails
        """
        pass

    @abstractmethod
    async def generate_embeddings_batch(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for multiple texts in batch.

        Batch processing is more efficient than individual calls.

        Args:
            texts: List of texts to embed

        Returns:
            list[list[float]]: List of vector embeddings

        Raises:
            ValueError: If texts list is empty
            RuntimeError: If embedding generation fails
        """
        pass

    @abstractmethod
    def get_embedding_dimension(self) -> int:
        """Get the dimension of embeddings produced by this generator.

        Returns:
            int: Embedding dimension size
        """
        pass
