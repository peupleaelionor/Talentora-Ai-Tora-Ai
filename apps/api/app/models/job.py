from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import (
    BigInteger,
    DateTime,
    Enum,
    Index,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

import enum


class RemoteType(str, enum.Enum):
    remote = "remote"
    onsite = "onsite"
    hybrid = "hybrid"
    unknown = "unknown"


class JobStatus(str, enum.Enum):
    active = "active"
    expired = "expired"
    duplicate = "duplicate"
    pending = "pending"


class JobOffer(Base):
    __tablename__ = "job_offers"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    # Source tracking
    source: Mapped[str] = mapped_column(String(100), nullable=False)
    source_job_id: Mapped[Optional[str]] = mapped_column(String(255))
    source_url: Mapped[Optional[str]] = mapped_column(Text)
    application_url: Mapped[Optional[str]] = mapped_column(Text)

    # Core fields
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    company_name: Mapped[Optional[str]] = mapped_column(String(500))
    company_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )

    # Location
    city: Mapped[Optional[str]] = mapped_column(String(200))
    region: Mapped[Optional[str]] = mapped_column(String(200))
    country: Mapped[Optional[str]] = mapped_column(String(100))

    # Work arrangement
    remote_type: Mapped[RemoteType] = mapped_column(
        Enum(RemoteType, name="remote_type_enum"),
        nullable=False,
        default=RemoteType.unknown,
    )
    contract_type: Mapped[Optional[str]] = mapped_column(String(100))

    # Compensation
    salary_min: Mapped[Optional[float]] = mapped_column(Numeric(12, 2))
    salary_max: Mapped[Optional[float]] = mapped_column(Numeric(12, 2))
    salary_currency: Mapped[Optional[str]] = mapped_column(String(10))

    # Experience / seniority
    experience_level: Mapped[Optional[str]] = mapped_column(String(100))
    seniority: Mapped[Optional[str]] = mapped_column(String(100))

    # Description
    description_raw: Mapped[Optional[str]] = mapped_column(Text)
    description_clean: Mapped[Optional[str]] = mapped_column(Text)

    # AI/NLP extracted fields (stored as JSONB arrays)
    skills_raw: Mapped[Optional[List[str]]] = mapped_column(JSONB)
    skills_normalized: Mapped[Optional[List[str]]] = mapped_column(JSONB)
    technologies: Mapped[Optional[List[str]]] = mapped_column(JSONB)
    keywords: Mapped[Optional[List[str]]] = mapped_column(JSONB)
    responsibilities: Mapped[Optional[List[str]]] = mapped_column(JSONB)
    benefits: Mapped[Optional[List[str]]] = mapped_column(JSONB)

    # Metadata
    language: Mapped[Optional[str]] = mapped_column(String(10))
    status: Mapped[JobStatus] = mapped_column(
        Enum(JobStatus, name="job_status_enum"),
        nullable=False,
        default=JobStatus.pending,
    )
    dedupe_hash: Mapped[Optional[str]] = mapped_column(String(64))

    # Dates
    posted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    scraped_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    job_skills: Mapped[List["JobSkill"]] = relationship(
        "JobSkill", back_populates="job", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("ix_job_offers_company_id", "company_id"),
        Index("ix_job_offers_country", "country"),
        Index("ix_job_offers_city", "city"),
        Index("ix_job_offers_region", "region"),
        Index("ix_job_offers_posted_at", "posted_at"),
        Index("ix_job_offers_status", "status"),
        Index("ix_job_offers_dedupe_hash", "dedupe_hash", unique=True),
        Index("ix_job_offers_source", "source"),
    )

    def __repr__(self) -> str:
        return f"<JobOffer id={self.id} title={self.title!r}>"
