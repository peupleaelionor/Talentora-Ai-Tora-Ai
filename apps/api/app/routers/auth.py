from __future__ import annotations

import uuid
from datetime import datetime

import structlog
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.user import User, Workspace
from app.schemas.auth import LoginRequest, RefreshRequest, RegisterRequest, TokenResponse, UserResponse
from app.services.auth_service import AuthService

logger = structlog.get_logger(__name__)
router = APIRouter()


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user and workspace",
)
async def register(
    payload: RegisterRequest,
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    service = AuthService(db)
    user = await service.register(payload)
    logger.info("User registered", user_id=str(user.id), email=user.email)
    return UserResponse.model_validate(user)


@router.post("/login", response_model=TokenResponse, summary="Obtain JWT tokens")
async def login(
    payload: LoginRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    service = AuthService(db)
    tokens = await service.login(payload.email, payload.password)
    if tokens is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    logger.info("User logged in", email=payload.email)
    return tokens


@router.post("/refresh", response_model=TokenResponse, summary="Refresh access token")
async def refresh(
    payload: RefreshRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    service = AuthService(db)
    tokens = await service.refresh(payload.refresh_token)
    if tokens is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )
    return tokens


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT, summary="Invalidate refresh token")
async def logout(
    payload: RefreshRequest,
    current_user: User = Depends(get_current_user),
) -> None:
    # Stateless JWT — client is responsible for discarding the token.
    # Extend here to implement a token denylist (Redis) if required.
    logger.info("User logged out", user_id=str(current_user.id))


@router.get("/me", response_model=UserResponse, summary="Get current user profile")
async def me(current_user: User = Depends(get_current_user)) -> UserResponse:
    return UserResponse.model_validate(current_user)
