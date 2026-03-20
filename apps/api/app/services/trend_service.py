from __future__ import annotations

from datetime import date
from typing import Any, Dict, List, Optional

import structlog
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.analytics import TrendMetric, SalaryStats, TrendGranularity

logger = structlog.get_logger(__name__)


class TrendService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def skill_trends(
        self,
        skills: List[str],
        country: Optional[str],
        granularity: str,
        periods: int,
    ) -> List[Dict[str, Any]]:
        results = []
        for skill in skills:
            stmt = (
                select(TrendMetric)
                .where(
                    TrendMetric.dimension == "skill",
                    TrendMetric.dimension_value == skill,
                    TrendMetric.granularity == granularity,
                )
                .order_by(TrendMetric.period_start.desc())
                .limit(periods)
            )
            if country:
                stmt = stmt.where(TrendMetric.country == country)

            rows = (await self.db.execute(stmt)).scalars().all()
            data_points = [
                {
                    "period": row.period_start.isoformat(),
                    "value": row.posting_count,
                    "yoy_growth_pct": float(row.yoy_growth_pct) if row.yoy_growth_pct else None,
                }
                for row in reversed(rows)
            ]
            results.append(
                {
                    "dimension": "skill",
                    "dimension_value": skill,
                    "country": country,
                    "granularity": granularity,
                    "data": data_points,
                }
            )
        return results

    async def salary_trends(
        self,
        country: Optional[str],
        job_title: Optional[str],
        seniority: Optional[str],
        granularity: str,
        periods: int,
    ) -> Dict[str, Any]:
        stmt = (
            select(SalaryStats)
            .where(SalaryStats.granularity == granularity)
            .order_by(SalaryStats.period_start.desc())
            .limit(periods)
        )
        if country:
            stmt = stmt.where(SalaryStats.country == country)
        if job_title:
            stmt = stmt.where(SalaryStats.job_title_normalised.ilike(f"%{job_title}%"))
        if seniority:
            stmt = stmt.where(SalaryStats.seniority == seniority)

        rows = (await self.db.execute(stmt)).scalars().all()
        return {
            "country": country,
            "job_title": job_title,
            "seniority": seniority,
            "granularity": granularity,
            "data": [
                {
                    "period": row.period_start.isoformat(),
                    "salary_p25": float(row.salary_p25) if row.salary_p25 else None,
                    "salary_median": float(row.salary_median) if row.salary_median else None,
                    "salary_p75": float(row.salary_p75) if row.salary_p75 else None,
                    "sample_size": row.sample_size,
                }
                for row in reversed(rows)
            ],
        }

    async def market_overview(self, country: Optional[str]) -> Dict[str, Any]:
        from sqlalchemy import and_
        from app.models.job import JobOffer, JobStatus

        stmt = select(func.count(JobOffer.id)).where(JobOffer.status == JobStatus.active)
        if country:
            stmt = stmt.where(JobOffer.country == country)
        active_jobs = (await self.db.execute(stmt)).scalar_one()

        top_skills_stmt = (
            select(TrendMetric.dimension_value, func.sum(TrendMetric.posting_count).label("total"))
            .where(TrendMetric.dimension == "skill")
            .group_by(TrendMetric.dimension_value)
            .order_by(func.sum(TrendMetric.posting_count).desc())
            .limit(10)
        )
        if country:
            top_skills_stmt = top_skills_stmt.where(TrendMetric.country == country)

        top_skills_rows = (await self.db.execute(top_skills_stmt)).all()
        top_skills = [{"skill": row[0], "count": int(row[1])} for row in top_skills_rows]

        return {
            "country": country,
            "active_job_count": active_jobs,
            "top_skills": top_skills,
        }

    async def hiring_velocity(
        self,
        country: Optional[str],
        sector: Optional[str],
        granularity: str,
        periods: int,
    ) -> Dict[str, Any]:
        stmt = (
            select(TrendMetric)
            .where(
                TrendMetric.dimension == "sector",
                TrendMetric.granularity == granularity,
            )
            .order_by(TrendMetric.period_start.desc())
            .limit(periods)
        )
        if country:
            stmt = stmt.where(TrendMetric.country == country)
        if sector:
            stmt = stmt.where(TrendMetric.dimension_value == sector)

        rows = (await self.db.execute(stmt)).scalars().all()
        return {
            "country": country,
            "sector": sector,
            "granularity": granularity,
            "data": [
                {
                    "period": row.period_start.isoformat(),
                    "posting_count": row.posting_count,
                    "yoy_growth_pct": float(row.yoy_growth_pct) if row.yoy_growth_pct else None,
                }
                for row in reversed(rows)
            ],
        }
