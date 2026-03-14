"""Response models for API endpoints."""

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = Field(..., description="Health status")
    version: str = Field(..., description="API version")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class DocumentResponse(BaseModel):
    """Document response model."""

    id: str = Field(..., description="Document ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    metadata: dict[str, Any] = Field(default_factory=dict)


class IngestionResponse(BaseModel):
    """Response for document ingestion."""

    document_id: str = Field(..., description="Document ID")
    chunks_created: int = Field(..., description="Number of chunks created")
    status: str = Field(..., description="Ingestion status")
    chunk_ids: list[str] = Field(default_factory=list, description="List of chunk IDs")


class SearchResultItem(BaseModel):
    """Single search result item."""

    chunk_id: str = Field(..., description="Chunk ID")
    document_id: str = Field(..., description="Document ID")
    content: str = Field(..., description="Chunk content")
    score: float = Field(..., ge=0.0, le=1.0, description="Similarity score")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Metadata")


class SearchResponse(BaseModel):
    """Search response with results."""

    query: str = Field(..., description="Original search query")
    results: list[SearchResultItem] = Field(
        default_factory=list, description="Search results"
    )
    total_results: int = Field(..., description="Total number of results")
    summary: Optional[str] = Field(None, description="Optional LLM-generated summary")
    cached: bool = Field(default=False, description="Whether results were cached")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "query": "machine learning",
                    "results": [
                        {
                            "chunk_id": "doc1_chunk_0",
                            "document_id": "doc1",
                            "content": "Machine learning is a subset of AI...",
                            "score": 0.95,
                            "metadata": {},
                        }
                    ],
                    "total_results": 1,
                    "summary": None,
                    "cached": False,
                }
            ]
        }
    }


class DocumentStatsResponse(BaseModel):
    """Document statistics response."""

    document_id: str = Field(..., description="Document ID")
    chunk_count: int = Field(..., description="Number of chunks")
    exists: bool = Field(..., description="Whether document exists")


class ErrorResponse(BaseModel):
    """Error response model."""

    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
