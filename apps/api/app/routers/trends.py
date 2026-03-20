from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.user import User
from app.services.trend_service import TrendService

router = APIRouter()


class TrendDataPoint(BaseModel):
    period: str
    value: float
    yoy_growth_pct: Optional[float]


class TrendResponse(BaseModel):
    dimension: str
    dimension_value: str
    country: Optional[str]
    granularity: str
    data: List[TrendDataPoint]


@router.get("/skills", response_model=List[TrendResponse], summary="Skill demand trends over time")
async def skill_trends(
    skills: List[str] = Query(..., description="Skill slugs to analyse"),
    country: Optional[str] = Query(None),
    granularity: str = Query("monthly", enum=["daily", "weekly", "monthly", "quarterly"]),
    periods: int = Query(12, ge=1, le=60),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[TrendResponse]:
    service = TrendService(db)
    return await service.skill_trends(skills, country, granularity, periods)


@router.get("/salary", summary="Salary benchmark trends")
async def salary_trends(
    country: Optional[str] = Query(None),
    job_title: Optional[str] = Query(None),
    seniority: Optional[str] = Query(None),
    granularity: str = Query("monthly", enum=["monthly", "quarterly"]),
    periods: int = Query(12, ge=1, le=24),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    service = TrendService(db)
    return await service.salary_trends(country, job_title, seniority, granularity, periods)


@router.get("/market-overview", summary="High-level market overview metrics")
async def market_overview(
    country: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    service = TrendService(db)
    return await service.market_overview(country)


@router.get("/hiring-velocity", summary="Job posting velocity by sector/location")
async def hiring_velocity(
    country: Optional[str] = Query(None),
    sector: Optional[str] = Query(None),
    granularity: str = Query("weekly"),
    periods: int = Query(12, ge=1, le=52),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    service = TrendService(db)
    return await service.hiring_velocity(country, sector, granularity, periods)
