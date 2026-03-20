from __future__ import annotations

import uuid
from typing import Any, Dict, List, Optional

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, ConfigDict
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import get_current_user, require_role
from app.models.user import User, UserRole

logger = structlog.get_logger(__name__)
router = APIRouter()


class UserAdminResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: str
    role: str
    is_active: bool
    is_verified: bool
    workspace_id: uuid.UUID


class WorkspaceAdminResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    slug: str
    subscription_tier: str
    is_active: bool


@router.get("/users", response_model=List[UserAdminResponse], summary="List all platform users")
async def list_all_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.admin)),
) -> List[UserAdminResponse]:
    from sqlalchemy import select

    stmt = (
        select(User)
        .order_by(User.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    result = await db.execute(stmt)
    users = result.scalars().all()
    return [UserAdminResponse.model_validate(u) for u in users]


@router.patch("/users/{user_id}/deactivate", summary="Deactivate a user account")
async def deactivate_user(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.admin)),
) -> dict:
    from sqlalchemy import select

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_active = False
    logger.info("User deactivated", target_user_id=str(user_id), by=str(current_user.id))
    return {"deactivated": True}


@router.get("/workspaces", response_model=List[WorkspaceAdminResponse], summary="List all workspaces")
async def list_workspaces(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.admin)),
) -> List[WorkspaceAdminResponse]:
    from sqlalchemy import select
    from app.models.user import Workspace

    stmt = (
        select(Workspace)
        .order_by(Workspace.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    result = await db.execute(stmt)
    workspaces = result.scalars().all()
    return [WorkspaceAdminResponse.model_validate(w) for w in workspaces]


@router.get("/stats", summary="Platform-level aggregate stats")
async def platform_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.admin)),
) -> Dict[str, Any]:
    from sqlalchemy import select, func
    from app.models.job import JobOffer
    from app.models.user import Workspace

    job_count = (await db.execute(select(func.count(JobOffer.id)))).scalar_one()
    workspace_count = (await db.execute(select(func.count(Workspace.id)))).scalar_one()
    user_count = (await db.execute(select(func.count(User.id)))).scalar_one()

    return {
        "total_jobs": job_count,
        "total_workspaces": workspace_count,
        "total_users": user_count,
    }
