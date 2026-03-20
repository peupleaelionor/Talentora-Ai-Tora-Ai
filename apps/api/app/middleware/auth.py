from __future__ import annotations

from typing import Callable

import structlog
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

from app.config import settings
from app.database import AsyncSessionLocal
from app.models.user import User, UserRole

logger = structlog.get_logger(__name__)

_bearer_scheme = HTTPBearer(auto_error=False)

# Paths that do not require authentication
_PUBLIC_PATHS = frozenset(
    [
        "/health",
        "/metrics",
        f"/api/{settings.API_VERSION}/auth/login",
        f"/api/{settings.API_VERSION}/auth/register",
        f"/api/{settings.API_VERSION}/auth/refresh",
        "/docs",
        "/redoc",
        f"/api/{settings.API_VERSION}/openapi.json",
    ]
)


class AuthMiddleware(BaseHTTPMiddleware):
    """Lightweight middleware that attaches structured log context for authenticated requests."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(
            method=request.method,
            path=request.url.path,
        )
        response = await call_next(request)
        return response


async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
    db: AsyncSession = Depends(lambda: None),  # replaced below via override
) -> User:
    raise NotImplementedError("Use the actual get_current_user dependency")


# Real implementation used via Depends
async def _get_db_for_auth() -> AsyncSession:  # type: ignore[return]
    async with AsyncSessionLocal() as session:
        yield session


async def get_current_user(  # type: ignore[no-redef]
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
    db: AsyncSession = Depends(_get_db_for_auth),
) -> User:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if payload.get("type") != "access":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")

    user_id: str | None = payload.get("sub")
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive")

    structlog.contextvars.bind_contextvars(user_id=str(user.id), workspace_id=str(user.workspace_id))
    return user


def require_role(*roles: UserRole) -> Callable:
    """Dependency factory that enforces minimum role requirements."""

    async def _check(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return current_user

    return _check
