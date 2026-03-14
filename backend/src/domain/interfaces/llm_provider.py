"""Interface for LLM providers."""

from abc import ABC, abstractmethod


class ILLMProvider(ABC):
    """Abstract interface for Large Language Model providers.

    This interface defines the contract for LLM implementations.
    Implementations might use Ollama, OpenAI, Anthropic, etc.
    """

    @abstractmethod
    async def summarize(self, context: str, query: str) -> str:
        """Generate a summary of search results.

        Args:
            context: Combined text from search results
            query: Original search query

        Returns:
            str: Generated summary

        Raises:
            ValueError: If context or query is empty
            RuntimeError: If LLM call fails
        """
        pass

    @abstractmethod
    async def answer_question(
        self, question: str, context: str, max_tokens: int = 500
    ) -> str:
        """Answer a question based on provided context.

        Args:
            question: Question to answer
            context: Context containing relevant information
            max_tokens: Maximum tokens in response

        Returns:
            str: Generated answer

        Raises:
            ValueError: If question or context is empty
            RuntimeError: If LLM call fails
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if the LLM provider is available.

        Returns:
            bool: True if provider is reachable and configured
        """
        pass
