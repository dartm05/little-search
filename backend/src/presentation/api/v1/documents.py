"""Document management endpoints."""

import logging
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status

from application.services import IngestionService
from domain.entities import Document
from presentation.api.models import (
    DocumentResponse,
    DocumentStatsResponse,
    DocumentUploadRequest,
    ErrorResponse,
    IngestionResponse,
)
from presentation.dependencies import get_ingestion_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/documents", tags=["documents"])


@router.post(
    "",
    response_model=IngestionResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
async def upload_document(
    request: DocumentUploadRequest,
    ingestion_service: IngestionService = Depends(get_ingestion_service),
) -> IngestionResponse:
    """Upload and index a new document.

    Args:
        request: Document upload request
        ingestion_service: Ingestion service dependency

    Returns:
        IngestionResponse: Ingestion results

    Raises:
        HTTPException: If ingestion fails
    """
    try:
        # Create document entity
        document = Document(
            id=str(uuid.uuid4()),
            content=request.content,
            metadata=request.metadata,
            created_at=datetime.utcnow(),
        )

        logger.info(f"Ingesting document: {document.id}")

        # Ingest document
        result = await ingestion_service.ingest_document(document)

        return IngestionResponse(**result)

    except ValueError as e:
        logger.error(f"Invalid document: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to ingest document: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to ingest document",
        )


@router.delete(
    "/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
async def delete_document(
    document_id: str,
    ingestion_service: IngestionService = Depends(get_ingestion_service),
) -> None:
    """Delete a document and all its chunks.

    Args:
        document_id: ID of document to delete
        ingestion_service: Ingestion service dependency

    Raises:
        HTTPException: If deletion fails
    """
    try:
        logger.info(f"Deleting document: {document_id}")
        success = await ingestion_service.delete_document(document_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Document not found"
            )

    except ValueError as e:
        logger.error(f"Invalid document ID: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete document: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete document",
        )


@router.get(
    "/{document_id}/stats",
    response_model=DocumentStatsResponse,
    responses={
        500: {"model": ErrorResponse},
    },
)
async def get_document_stats(
    document_id: str,
    ingestion_service: IngestionService = Depends(get_ingestion_service),
) -> DocumentStatsResponse:
    """Get statistics for a document.

    Args:
        document_id: ID of document
        ingestion_service: Ingestion service dependency

    Returns:
        DocumentStatsResponse: Document statistics

    Raises:
        HTTPException: If operation fails
    """
    try:
        logger.info(f"Getting stats for document: {document_id}")
        stats = await ingestion_service.get_document_stats(document_id)
        return DocumentStatsResponse(**stats)

    except Exception as e:
        logger.error(f"Failed to get document stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get document stats",
        )
