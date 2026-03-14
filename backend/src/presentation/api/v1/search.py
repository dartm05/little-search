"""Search endpoints."""

import logging

from fastapi import APIRouter, Depends, HTTPException, Query, status

from application.services import SearchService
from presentation.api.models import ErrorResponse, SearchRequest, SearchResponse, SearchResultItem
from presentation.dependencies import get_search_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/search", tags=["search"])


@router.get(
    "",
    response_model=SearchResponse,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
async def search_documents(
    query: str = Query(..., min_length=1, description="Search query"),
    top_k: int = Query(10, ge=1, le=100, description="Number of results"),
    use_cache: bool = Query(True, description="Whether to use cache"),
    min_score: float | None = Query(None, ge=0.0, le=1.0, description="Minimum similarity score"),
    search_service: SearchService = Depends(get_search_service),
) -> SearchResponse:
    """Search for documents using semantic similarity.

    Args:
        query: Search query text
        top_k: Number of results to return
        use_cache: Whether to use cache
        search_service: Search service dependency

    Returns:
        SearchResponse: Search results

    Raises:
        HTTPException: If search fails
    """
    try:
        logger.info(f"Search request: '{query}' (top_k={top_k})")

        # Perform search
        results = await search_service.search(
            query=query, top_k=top_k, use_cache=use_cache, min_score=min_score
        )

        # Convert to response model
        result_items = [
            SearchResultItem(
                chunk_id=sr.chunk.id,
                document_id=sr.document.id,
                content=sr.chunk.content,
                score=sr.score,
                metadata=sr.chunk.metadata,
            )
            for sr in results
        ]

        return SearchResponse(
            query=query,
            results=result_items,
            total_results=len(result_items),
            summary=None,
            cached=False,
        )

    except ValueError as e:
        logger.error(f"Invalid search request: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Search failed"
        )


@router.post(
    "",
    response_model=SearchResponse,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
async def search_documents_advanced(
    request: SearchRequest,
    search_service: SearchService = Depends(get_search_service),
) -> SearchResponse:
    """Advanced search with filters and optional summarization.

    Args:
        request: Search request
        search_service: Search service dependency

    Returns:
        SearchResponse: Search results with optional summary

    Raises:
        HTTPException: If search fails
    """
    try:
        logger.info(
            f"Advanced search request: '{request.query}' (top_k={request.top_k}, "
            f"summary={request.use_summary})"
        )

        # Perform search with optional summary
        if request.use_summary:
            results, summary = await search_service.search_with_summary(
                query=request.query, top_k=request.top_k
            )
        else:
            results = await search_service.search(
                query=request.query,
                top_k=request.top_k,
                filter_conditions=request.filter_conditions,
                use_cache=request.use_cache,
            )
            summary = None

        # Convert to response model
        result_items = [
            SearchResultItem(
                chunk_id=sr.chunk.id,
                document_id=sr.document.id,
                content=sr.chunk.content,
                score=sr.score,
                metadata=sr.chunk.metadata,
            )
            for sr in results
        ]

        return SearchResponse(
            query=request.query,
            results=result_items,
            total_results=len(result_items),
            summary=summary,
            cached=False,
        )

    except ValueError as e:
        logger.error(f"Invalid search request: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Advanced search failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Search failed"
        )
