from __future__ import annotations

import hashlib
import uuid
from typing import List, Optional

import structlog
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.job import JobOffer, JobStatus
from app.schemas.job import JobOfferCreate, JobOfferListResponse, JobOfferResponse, JobOfferUpdate

logger = structlog.get_logger(__name__)


class JobService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def list_jobs(
        self,
        page: int = 1,
        page_size: int = 20,
        country: Optional[str] = None,
        city: Optional[str] = None,
        remote_type: Optional[str] = None,
        contract_type: Optional[str] = None,
        seniority: Optional[str] = None,
        skills: Optional[List[str]] = None,
        status: Optional[str] = None,
    ) -> JobOfferListResponse:
        stmt = select(JobOffer)

        if country:
            stmt = stmt.where(JobOffer.country == country)
        if city:
            stmt = stmt.where(JobOffer.city.ilike(f"%{city}%"))
        if remote_type:
            stmt = stmt.where(JobOffer.remote_type == remote_type)
        if contract_type:
            stmt = stmt.where(JobOffer.contract_type == contract_type)
        if seniority:
            stmt = stmt.where(JobOffer.seniority == seniority)
        if status:
            stmt = stmt.where(JobOffer.status == status)

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = (await self.db.execute(count_stmt)).scalar_one()

        stmt = stmt.order_by(JobOffer.posted_at.desc()).offset((page - 1) * page_size).limit(page_size)
        result = await self.db.execute(stmt)
        jobs = result.scalars().all()

        pages = max(1, -(-total // page_size))  # ceiling division
        return JobOfferListResponse(
            items=[JobOfferResponse.model_validate(j) for j in jobs],
            total=total,
            page=page,
            page_size=page_size,
            pages=pages,
        )

    async def create_job(self, payload: JobOfferCreate) -> JobOffer:
        dedupe_input = f"{payload.source}:{payload.source_job_id or payload.title}:{payload.company_name}"
        dedupe_hash = hashlib.sha256(dedupe_input.encode()).hexdigest()

        existing = await self.db.execute(
            select(JobOffer).where(JobOffer.dedupe_hash == dedupe_hash)
        )
        if existing.scalar_one_or_none():
            logger.info("Duplicate job detected, skipping", dedupe_hash=dedupe_hash)
            raise ValueError(f"Duplicate job offer (hash={dedupe_hash})")

        data = payload.model_dump()
        job = JobOffer(**data, dedupe_hash=dedupe_hash)
        self.db.add(job)
        await self.db.flush()
        return job

    async def get_job(self, job_id: uuid.UUID) -> Optional[JobOffer]:
        result = await self.db.execute(select(JobOffer).where(JobOffer.id == job_id))
        return result.scalar_one_or_none()

    async def update_job(self, job_id: uuid.UUID, payload: JobOfferUpdate) -> Optional[JobOffer]:
        result = await self.db.execute(select(JobOffer).where(JobOffer.id == job_id))
        job = result.scalar_one_or_none()
        if job is None:
            return None

        update_data = payload.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(job, field, value)

        await self.db.flush()
        return job

    async def delete_job(self, job_id: uuid.UUID) -> bool:
        result = await self.db.execute(select(JobOffer).where(JobOffer.id == job_id))
        job = result.scalar_one_or_none()
        if job is None:
            return False
        await self.db.delete(job)
        await self.db.flush()
        return True
