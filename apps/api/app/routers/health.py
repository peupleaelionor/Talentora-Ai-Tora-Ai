from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db

router = APIRouter()


class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    database: str
    version: str


@router.get("", response_model=HealthResponse, summary="Liveness + readiness probe")
async def health_check(db: AsyncSession = Depends(get_db)) -> HealthResponse:
    db_status = "ok"
    try:
        await db.execute(text("SELECT 1"))
    except Exception:
        db_status = "unavailable"

    from app.config import settings

    return HealthResponse(
        status="ok",
        timestamp=datetime.now(timezone.utc),
        database=db_status,
        version=settings.API_VERSION,
    )
