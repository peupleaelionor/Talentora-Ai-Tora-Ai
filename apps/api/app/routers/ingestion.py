from __future__ import annotations

from typing import Any, Dict, Optional

import structlog
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import require_role
from app.models.user import User, UserRole

logger = structlog.get_logger(__name__)
router = APIRouter()


class IngestionTriggerRequest(BaseModel):
    source: str
    country: Optional[str] = None
    max_pages: int = 10
    parameters: Optional[Dict[str, Any]] = None


class IngestionStatusResponse(BaseModel):
    task_id: str
    source: str
    status: str
    message: str


@router.post(
    "/trigger",
    response_model=IngestionStatusResponse,
    summary="Trigger a scraping job for a given source",
)
async def trigger_ingestion(
    payload: IngestionTriggerRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.admin)),
) -> IngestionStatusResponse:
    SUPPORTED_SOURCES = {"linkedin", "indeed", "glassdoor", "stepstone", "monster", "xing"}
    if payload.source not in SUPPORTED_SOURCES:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown source '{payload.source}'. Supported: {sorted(SUPPORTED_SOURCES)}",
        )

    # Dispatch Celery task (stub — celery app wired separately)
    task_id = f"stub-{payload.source}-{payload.country or 'eu'}"
    logger.info(
        "Ingestion triggered",
        source=payload.source,
        country=payload.country,
        triggered_by=str(current_user.id),
    )
    return IngestionStatusResponse(
        task_id=task_id,
        source=payload.source,
        status="queued",
        message="Ingestion task queued successfully",
    )


@router.get("/status/{task_id}", summary="Poll ingestion task status")
async def ingestion_status(
    task_id: str,
    current_user: User = Depends(require_role(UserRole.admin)),
) -> Dict[str, Any]:
    # In production query Celery/Redis for task state
    return {"task_id": task_id, "status": "unknown", "detail": "Celery integration pending"}


@router.get("/sources", summary="List available ingestion sources")
async def list_sources(
    current_user: User = Depends(require_role(UserRole.admin)),
) -> Dict[str, Any]:
    return {
        "sources": [
            {"name": "linkedin", "region": "global"},
            {"name": "indeed", "region": "global"},
            {"name": "glassdoor", "region": "global"},
            {"name": "stepstone", "region": "europe"},
            {"name": "monster", "region": "europe"},
            {"name": "xing", "region": "dach"},
        ]
    }
