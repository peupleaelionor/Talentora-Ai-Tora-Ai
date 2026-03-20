from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.user import User

logger = structlog.get_logger(__name__)
router = APIRouter()


class ReportCreateRequest(BaseModel):
    title: str
    report_type: str
    format: str = "pdf"
    parameters: Optional[Dict[str, Any]] = None


class ReportResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    report_type: str
    status: str
    format: str
    download_url: Optional[str]
    created_at: datetime
    completed_at: Optional[datetime]


@router.post(
    "",
    response_model=ReportResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Queue a new report for generation",
)
async def create_report(
    payload: ReportCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ReportResponse:
    from app.models.report import Report, ReportStatus, ReportFormat

    report = Report(
        workspace_id=current_user.workspace_id,
        created_by_id=current_user.id,
        title=payload.title,
        report_type=payload.report_type,
        parameters=payload.parameters,
        status=ReportStatus.queued,
        format=ReportFormat(payload.format),
    )
    db.add(report)
    await db.flush()
    logger.info("Report queued", report_id=str(report.id), type=report.report_type)
    # Celery task would be dispatched here
    return ReportResponse.model_validate(report)


@router.get("", response_model=List[ReportResponse], summary="List reports for the workspace")
async def list_reports(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[ReportResponse]:
    from sqlalchemy import select
    from app.models.report import Report

    stmt = (
        select(Report)
        .where(Report.workspace_id == current_user.workspace_id)
        .order_by(Report.created_at.desc())
    )
    result = await db.execute(stmt)
    reports = result.scalars().all()
    return [ReportResponse.model_validate(r) for r in reports]


@router.get("/{report_id}", response_model=ReportResponse, summary="Get report details and download URL")
async def get_report(
    report_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ReportResponse:
    from sqlalchemy import select
    from app.models.report import Report

    stmt = select(Report).where(
        Report.id == report_id,
        Report.workspace_id == current_user.workspace_id,
    )
    result = await db.execute(stmt)
    report = result.scalar_one_or_none()
    if report is None:
        raise HTTPException(status_code=404, detail="Report not found")
    return ReportResponse.model_validate(report)
