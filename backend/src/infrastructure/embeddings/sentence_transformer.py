"""Sentence Transformer implementation for embeddings."""

import logging
from typing import Optional

from sentence_transformers import SentenceTransformer

from domain.interfaces import IEmbeddingGenerator

logger = logging.getLogger(__name__)


class SentenceTransformerEmbeddings(IEmbeddingGenerator):
    """Embedding generator using sentence-transformers library.

    This implementation uses local models from HuggingFace for generating
    embeddings without requiring external API calls.
    """

    def __init__(self, model_name: str, dimension: int):
        """Initialize the sentence transformer.

        Args:
            model_name: Name of the sentence-transformers model
            dimension: Expected embedding dimension
        """
        self._model_name = model_name
        self._dimension = dimension
        self._model: Optional[SentenceTransformer] = None
        logger.info(f"Initializing SentenceTransformer with model: {model_name}")

    def _ensure_model_loaded(self) -> SentenceTransformer:
        """Lazy load the model on first use.

        Returns:
            SentenceTransformer: Loaded model

        Raises:
            RuntimeError: If model loading fails
        """
        if self._model is None:
            try:
                self._model = SentenceTransformer(self._model_name)
                logger.info(f"Model {self._model_name} loaded successfully")
            except Exception as e:
                logger.error(f"Failed to load model {self._model_name}: {e}")
                raise RuntimeError(f"Failed to load embedding model: {e}") from e
        return self._model

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
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")

        try:
            model = self._ensure_model_loaded()
            embedding = model.encode(text, convert_to_numpy=True)
            return embedding.tolist()
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            raise RuntimeError(f"Embedding generation failed: {e}") from e

    async def generate_embeddings_batch(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for multiple texts in batch.

        Args:
            texts: List of texts to embed

        Returns:
            list[list[float]]: List of vector embeddings

        Raises:
            ValueError: If texts list is empty
            RuntimeError: If embedding generation fails
        """
        if not texts:
            raise ValueError("Texts list cannot be empty")

        # Filter out empty texts
        valid_texts = [t for t in texts if t and t.strip()]
        if not valid_texts:
            raise ValueError("All texts are empty")

        try:
            model = self._ensure_model_loaded()
            embeddings = model.encode(
                valid_texts, convert_to_numpy=True, show_progress_bar=False
            )
            return embeddings.tolist()
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Failed to generate batch embeddings: {e}")
            raise RuntimeError(f"Batch embedding generation failed: {e}") from e

    def get_embedding_dimension(self) -> int:
        """Get the dimension of embeddings produced by this generator.

        Returns:
            int: Embedding dimension size
        """
        return self._dimension
