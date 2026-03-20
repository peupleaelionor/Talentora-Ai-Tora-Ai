from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

import structlog
from fastapi import HTTPException, status
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.user import User, Workspace
from app.schemas.auth import RegisterRequest, TokenResponse

logger = structlog.get_logger(__name__)

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain: str) -> str:
    return _pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    return _pwd_context.verify(plain, hashed)


def create_access_token(subject: str, extra_claims: Optional[Dict[str, Any]] = None) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload: Dict[str, Any] = {"sub": subject, "exp": expire, "type": "access"}
    if extra_claims:
        payload.update(extra_claims)
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(subject: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    payload: Dict[str, Any] = {"sub": subject, "exp": expire, "type": "refresh"}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str) -> Dict[str, Any]:
    """Decode and validate a JWT. Raises HTTPException on failure."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


class AuthService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def register(self, payload: RegisterRequest) -> User:
        # Check for existing email
        existing = await self.db.execute(select(User).where(User.email == payload.email))
        if existing.scalar_one_or_none():
            raise HTTPException(status_code=409, detail="Email already registered")

        workspace = Workspace(
            name=payload.workspace_name,
            slug=payload.workspace_name.lower().replace(" ", "-"),
        )
        self.db.add(workspace)
        await self.db.flush()

        user = User(
            workspace_id=workspace.id,
            email=payload.email,
            hashed_password=hash_password(payload.password),
            first_name=payload.first_name,
            last_name=payload.last_name,
        )
        from app.models.user import UserRole
        user.role = UserRole.owner

        self.db.add(user)
        await self.db.flush()
        return user

    async def login(self, email: str, password: str) -> Optional[TokenResponse]:
        result = await self.db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        if user is None or not verify_password(password, user.hashed_password):
            return None
        if not user.is_active:
            raise HTTPException(status_code=403, detail="Account is deactivated")

        user.last_login_at = datetime.now(timezone.utc)
        await self.db.flush()

        return self._build_tokens(str(user.id))

    async def refresh(self, refresh_token: str) -> Optional[TokenResponse]:
        try:
            payload = decode_token(refresh_token)
        except HTTPException:
            return None

        if payload.get("type") != "refresh":
            return None

        user_id = payload.get("sub")
        if not user_id:
            return None

        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if user is None or not user.is_active:
            return None

        return self._build_tokens(str(user.id))

    def _build_tokens(self, user_id: str) -> TokenResponse:
        return TokenResponse(
            access_token=create_access_token(user_id),
            refresh_token=create_refresh_token(user_id),
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )
