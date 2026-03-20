from __future__ import annotations

import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, ConfigDict
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.user import User

router = APIRouter()


class SkillResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    slug: str
    category: str
    aliases: Optional[str]
    description: Optional[str]


class SkillListResponse(BaseModel):
    items: List[SkillResponse]
    total: int


@router.get("", response_model=SkillListResponse, summary="List all skills")
async def list_skills(
    category: Optional[str] = Query(None),
    q: Optional[str] = Query(None, description="Search by name"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SkillListResponse:
    from sqlalchemy import select, func
    from app.models.skill import Skill

    stmt = select(Skill)
    if category:
        stmt = stmt.where(Skill.category == category)
    if q:
        stmt = stmt.where(Skill.name.ilike(f"%{q}%"))

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total_result = await db.execute(count_stmt)
    total = total_result.scalar_one()

    stmt = stmt.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(stmt)
    skills = result.scalars().all()

    return SkillListResponse(
        items=[SkillResponse.model_validate(s) for s in skills],
        total=total,
    )


@router.get("/{skill_id}", response_model=SkillResponse, summary="Get a skill by ID")
async def get_skill(
    skill_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SkillResponse:
    from sqlalchemy import select
    from app.models.skill import Skill

    result = await db.execute(select(Skill).where(Skill.id == skill_id))
    skill = result.scalar_one_or_none()
    if skill is None:
        raise HTTPException(status_code=404, detail="Skill not found")
    return SkillResponse.model_validate(skill)


@router.get("/{skill_id}/demand", summary="Get demand trend for a specific skill")
async def skill_demand(
    skill_id: uuid.UUID,
    country: Optional[str] = Query(None),
    granularity: str = Query("monthly"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    # Placeholder — computed via TrendService in a real implementation
    return {"skill_id": str(skill_id), "country": country, "granularity": granularity, "data": []}
