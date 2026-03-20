from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Enum, ForeignKey, Index, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

import enum


class SkillCategory(str, enum.Enum):
    programming_language = "programming_language"
    framework = "framework"
    cloud = "cloud"
    database = "database"
    devops = "devops"
    soft_skill = "soft_skill"
    domain = "domain"
    tool = "tool"
    other = "other"


class Skill(Base):
    __tablename__ = "skills"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    name: Mapped[str] = mapped_column(String(300), nullable=False, unique=True)
    slug: Mapped[str] = mapped_column(String(300), nullable=False, unique=True)
    category: Mapped[SkillCategory] = mapped_column(
        Enum(SkillCategory, name="skill_category_enum"),
        nullable=False,
        default=SkillCategory.other,
    )
    aliases: Mapped[Optional[str]] = mapped_column(String(1000))
    description: Mapped[Optional[str]] = mapped_column(String(2000))

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    job_skills: Mapped[list["JobSkill"]] = relationship(
        "JobSkill", back_populates="skill", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("ix_skills_name", "name"),
        Index("ix_skills_slug", "slug"),
        Index("ix_skills_category", "category"),
    )

    def __repr__(self) -> str:
        return f"<Skill id={self.id} name={self.name!r}>"


class JobSkill(Base):
    __tablename__ = "job_skills"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("job_offers.id", ondelete="CASCADE"),
        nullable=False,
    )
    skill_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("skills.id", ondelete="CASCADE"),
        nullable=False,
    )
    # Confidence score from NLP extraction (0.0–1.0)
    confidence: Mapped[Optional[float]] = mapped_column(default=1.0)
    is_required: Mapped[bool] = mapped_column(default=True, nullable=False)

    job: Mapped["JobOffer"] = relationship("JobOffer", back_populates="job_skills")  # noqa: F821
    skill: Mapped["Skill"] = relationship("Skill", back_populates="job_skills")

    __table_args__ = (
        Index("ix_job_skills_job_id", "job_id"),
        Index("ix_job_skills_skill_id", "skill_id"),
    )
