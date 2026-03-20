from __future__ import annotations

import uuid
from typing import List, Optional

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.user import User
from app.schemas.job import JobOfferCreate, JobOfferListResponse, JobOfferResponse, JobOfferUpdate
from app.services.job_service import JobService

logger = structlog.get_logger(__name__)
router = APIRouter()


@router.get("", response_model=JobOfferListResponse, summary="List job offers with pagination and filters")
async def list_jobs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    country: Optional[str] = Query(None),
    city: Optional[str] = Query(None),
    remote_type: Optional[str] = Query(None),
    contract_type: Optional[str] = Query(None),
    seniority: Optional[str] = Query(None),
    skills: Optional[List[str]] = Query(None),
    status: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> JobOfferListResponse:
    service = JobService(db)
    return await service.list_jobs(
        page=page,
        page_size=page_size,
        country=country,
        city=city,
        remote_type=remote_type,
        contract_type=contract_type,
        seniority=seniority,
        skills=skills,
        status=status,
    )


@router.post(
    "",
    response_model=JobOfferResponse,
    status_code=201,
    summary="Create a new job offer",
)
async def create_job(
    payload: JobOfferCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> JobOfferResponse:
    service = JobService(db)
    job = await service.create_job(payload)
    logger.info("Job created", job_id=str(job.id))
    return JobOfferResponse.model_validate(job)


@router.get("/{job_id}", response_model=JobOfferResponse, summary="Get a single job offer")
async def get_job(
    job_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> JobOfferResponse:
    service = JobService(db)
    job = await service.get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return JobOfferResponse.model_validate(job)


@router.patch("/{job_id}", response_model=JobOfferResponse, summary="Partially update a job offer")
async def update_job(
    job_id: uuid.UUID,
    payload: JobOfferUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> JobOfferResponse:
    service = JobService(db)
    job = await service.update_job(job_id, payload)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return JobOfferResponse.model_validate(job)


@router.delete("/{job_id}", status_code=204, summary="Delete a job offer")
async def delete_job(
    job_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    service = JobService(db)
    deleted = await service.delete_job(job_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Job not found")
