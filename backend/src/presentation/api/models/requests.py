"""Request models for API endpoints."""

from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator


class DocumentUploadRequest(BaseModel):
    """Request model for document upload."""

    content: str = Field(..., min_length=1, description="Document text content")
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Optional document metadata"
    )

    @field_validator("content")
    @classmethod
    def validate_content(cls, v: str) -> str:
        """Validate content is not empty."""
        if not v.strip():
            raise ValueError("Content cannot be empty or whitespace only")
        return v

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "content": "This is a sample document about machine learning.",
                    "metadata": {"title": "ML Introduction", "author": "John Doe"},
                }
            ]
        }
    }


class SearchRequest(BaseModel):
    """Request model for search."""

    query: str = Field(..., min_length=1, description="Search query")
    top_k: int = Field(default=10, ge=1, le=100, description="Number of results")
    filter_conditions: Optional[dict[str, Any]] = Field(
        default=None, description="Optional metadata filters"
    )
    use_cache: bool = Field(default=True, description="Whether to use cache")
    use_summary: bool = Field(
        default=False, description="Whether to generate LLM summary"
    )

    @field_validator("query")
    @classmethod
    def validate_query(cls, v: str) -> str:
        """Validate query is not empty."""
        if not v.strip():
            raise ValueError("Query cannot be empty or whitespace only")
        return v

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "query": "machine learning algorithms",
                    "top_k": 5,
                    "use_cache": True,
                    "use_summary": False,
                }
            ]
        }
    }
