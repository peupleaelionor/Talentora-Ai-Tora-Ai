from __future__ import annotations

import uuid
from datetime import datetime, date
from typing import Optional

from sqlalchemy import Date, DateTime, Enum, Index, Integer, Numeric, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base

import enum


class TrendGranularity(str, enum.Enum):
    daily = "daily"
    weekly = "weekly"
    monthly = "monthly"
    quarterly = "quarterly"


class SalaryStats(Base):
    """Pre-aggregated salary statistics by role/skill/location/period."""

    __tablename__ = "salary_stats"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    period_start: Mapped[date] = mapped_column(Date, nullable=False)
    period_end: Mapped[date] = mapped_column(Date, nullable=False)
    granularity: Mapped[TrendGranularity] = mapped_column(
        Enum(TrendGranularity, name="trend_granularity_enum"),
        nullable=False,
        default=TrendGranularity.monthly,
    )

    country: Mapped[Optional[str]] = mapped_column(String(100))
    city: Mapped[Optional[str]] = mapped_column(String(200))
    job_title_normalised: Mapped[Optional[str]] = mapped_column(String(300))
    skill_name: Mapped[Optional[str]] = mapped_column(String(300))
    seniority: Mapped[Optional[str]] = mapped_column(String(100))
    contract_type: Mapped[Optional[str]] = mapped_column(String(100))
    currency: Mapped[str] = mapped_column(String(10), nullable=False, default="EUR")

    salary_p10: Mapped[Optional[float]] = mapped_column(Numeric(12, 2))
    salary_p25: Mapped[Optional[float]] = mapped_column(Numeric(12, 2))
    salary_median: Mapped[Optional[float]] = mapped_column(Numeric(12, 2))
    salary_mean: Mapped[Optional[float]] = mapped_column(Numeric(12, 2))
    salary_p75: Mapped[Optional[float]] = mapped_column(Numeric(12, 2))
    salary_p90: Mapped[Optional[float]] = mapped_column(Numeric(12, 2))
    sample_size: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    computed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        Index("ix_salary_stats_period", "period_start", "period_end"),
        Index("ix_salary_stats_country", "country"),
        Index("ix_salary_stats_skill", "skill_name"),
    )


class TrendMetric(Base):
    """Time-series demand/posting count for a given dimension."""

    __tablename__ = "trend_metrics"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    period_start: Mapped[date] = mapped_column(Date, nullable=False)
    granularity: Mapped[TrendGranularity] = mapped_column(
        Enum(TrendGranularity, name="trend_granularity_enum"),
        nullable=False,
        default=TrendGranularity.monthly,
    )

    dimension: Mapped[str] = mapped_column(String(100), nullable=False)
    dimension_value: Mapped[str] = mapped_column(String(300), nullable=False)

    country: Mapped[Optional[str]] = mapped_column(String(100))
    posting_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    yoy_growth_pct: Mapped[Optional[float]] = mapped_column(Numeric(8, 4))

    computed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        Index("ix_trend_metrics_period", "period_start"),
        Index("ix_trend_metrics_dimension", "dimension", "dimension_value"),
        Index("ix_trend_metrics_country", "country"),
    )
