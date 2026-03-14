"""Batch operation models."""

from typing import Any, List

from pydantic import BaseModel, Field


class BatchDocumentRequest(BaseModel):
    """Request model for batch document upload."""

    documents: List[dict[str, Any]] = Field(
        ..., min_length=1, max_length=100, description="List of documents to upload"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "documents": [
                        {
                            "content": "First document content",
                            "metadata": {"title": "Doc 1"},
                        },
                        {
                            "content": "Second document content",
                            "metadata": {"title": "Doc 2"},
                        },
                    ]
                }
            ]
        }
    }


class BatchDocumentResult(BaseModel):
    """Result for a single document in batch operation."""

    document_id: str
    status: str
    chunks_created: int = 0
    error: str | None = None


class BatchIngestionResponse(BaseModel):
    """Response for batch document ingestion."""

    total_documents: int
    successful: int
    failed: int
    results: List[BatchDocumentResult]
