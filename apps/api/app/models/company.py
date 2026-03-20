from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import DateTime, Index, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Company(Base):
    __tablename__ = "companies"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    name: Mapped[str] = mapped_column(String(500), nullable=False)
    slug: Mapped[Optional[str]] = mapped_column(String(500), unique=True)
    website: Mapped[Optional[str]] = mapped_column(Text)
    linkedin_url: Mapped[Optional[str]] = mapped_column(Text)

    industry: Mapped[Optional[str]] = mapped_column(String(200))
    sub_industry: Mapped[Optional[str]] = mapped_column(String(200))
    company_size: Mapped[Optional[str]] = mapped_column(String(100))
    headquarters_country: Mapped[Optional[str]] = mapped_column(String(100))
    headquarters_city: Mapped[Optional[str]] = mapped_column(String(200))

    description: Mapped[Optional[str]] = mapped_column(Text)
    logo_url: Mapped[Optional[str]] = mapped_column(Text)

    # Tech stack / culture tags stored as JSONB arrays
    tech_stack: Mapped[Optional[List[str]]] = mapped_column(JSONB)
    culture_tags: Mapped[Optional[List[str]]] = mapped_column(JSONB)

    is_verified: Mapped[bool] = mapped_column(default=False, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    __table_args__ = (
        Index("ix_companies_name", "name"),
        Index("ix_companies_slug", "slug"),
        Index("ix_companies_industry", "industry"),
        Index("ix_companies_headquarters_country", "headquarters_country"),
    )

    def __repr__(self) -> str:
        return f"<Company id={self.id} name={self.name!r}>"
