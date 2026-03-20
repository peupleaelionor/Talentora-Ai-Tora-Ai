from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.job import JobOffer
from app.models.user import User
from app.schemas.job import JobOfferResponse

router = APIRouter()


class SearchResponse(BaseModel):
    items: List[JobOfferResponse]
    total: int
    query: str
    page: int
    page_size: int


@router.get("", response_model=SearchResponse, summary="Full-text search across job offers")
async def search_jobs(
    q: str = Query(..., min_length=1, description="Search query"),
    country: Optional[str] = Query(None),
    city: Optional[str] = Query(None),
    remote_type: Optional[str] = Query(None),
    contract_type: Optional[str] = Query(None),
    seniority: Optional[str] = Query(None),
    salary_min: Optional[float] = Query(None, ge=0),
    salary_max: Optional[float] = Query(None, ge=0),
    skills: Optional[List[str]] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SearchResponse:
    stmt = select(JobOffer).where(
        or_(
            JobOffer.title.ilike(f"%{q}%"),
            JobOffer.description_clean.ilike(f"%{q}%"),
            JobOffer.company_name.ilike(f"%{q}%"),
        )
    )

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
    if salary_min is not None:
        stmt = stmt.where(JobOffer.salary_max >= salary_min)
    if salary_max is not None:
        stmt = stmt.where(JobOffer.salary_min <= salary_max)

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = (await db.execute(count_stmt)).scalar_one()

    stmt = stmt.order_by(JobOffer.posted_at.desc()).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(stmt)
    jobs = result.scalars().all()

    return SearchResponse(
        items=[JobOfferResponse.model_validate(j) for j in jobs],
        total=total,
        query=q,
        page=page,
        page_size=page_size,
    )
