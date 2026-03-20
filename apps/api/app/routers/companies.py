from __future__ import annotations

import uuid
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.user import User

router = APIRouter()


class CompanyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    slug: Optional[str]
    industry: Optional[str]
    headquarters_country: Optional[str]
    headquarters_city: Optional[str]
    company_size: Optional[str]
    website: Optional[str]
    is_verified: bool
    created_at: datetime


class CompanyListResponse(BaseModel):
    items: List[CompanyResponse]
    total: int
    page: int
    page_size: int


@router.get("", response_model=CompanyListResponse, summary="List companies")
async def list_companies(
    q: Optional[str] = Query(None),
    industry: Optional[str] = Query(None),
    country: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CompanyListResponse:
    from sqlalchemy import func
    from app.models.company import Company

    stmt = select(Company)
    if q:
        stmt = stmt.where(Company.name.ilike(f"%{q}%"))
    if industry:
        stmt = stmt.where(Company.industry == industry)
    if country:
        stmt = stmt.where(Company.headquarters_country == country)

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = (await db.execute(count_stmt)).scalar_one()

    stmt = stmt.order_by(Company.name).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(stmt)
    companies = result.scalars().all()

    return CompanyListResponse(
        items=[CompanyResponse.model_validate(c) for c in companies],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{company_id}", response_model=CompanyResponse, summary="Get a company by ID")
async def get_company(
    company_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CompanyResponse:
    from app.models.company import Company

    result = await db.execute(select(Company).where(Company.id == company_id))
    company = result.scalar_one_or_none()
    if company is None:
        raise HTTPException(status_code=404, detail="Company not found")
    return CompanyResponse.model_validate(company)
