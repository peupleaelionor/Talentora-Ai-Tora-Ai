"""
Trend computation engine for the Talentora analytics package.

Computes rolling skill demand trends, salary trends by role/region,
regional demand maps, emerging skill detection, and remote work patterns
by querying the normalised job offer database.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any

import structlog

log = structlog.get_logger(__name__)

# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------


@dataclass
class SkillTrend:
    """Demand trend for a single skill over a time window."""

    skill_name: str
    demand_count: int
    growth_rate: float  # relative to previous equivalent period, e.g. 0.12 = +12 %
    avg_salary: float | None
    region: str | None
    timeframe: str
    computed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class SalaryTrend:
    """Salary trend for a canonical role in a region."""

    role: str
    region: str
    median_salary: float | None
    p25_salary: float | None
    p75_salary: float | None
    sample_count: int
    timeframe: str
    computed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class RegionDemand:
    """Demand for a specific skill broken down by region."""

    skill: str
    regions: dict[str, int]  # region code -> job count
    timeframe: str
    computed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class EmergingSkill:
    """A skill whose demand has grown faster than the threshold."""

    skill_name: str
    growth_rate: float
    absolute_count: int
    first_seen: datetime | None
    timeframe: str
    computed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class RemoteTrend:
    """Remote work adoption statistics."""

    remote_percentage: float
    partial_percentage: float
    onsite_percentage: float
    timeframe: str
    sample_count: int
    computed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _parse_timeframe(timeframe: str) -> timedelta:
    """Convert a timeframe string like ``"7d"``, ``"30d"``, ``"1y"`` to a timedelta."""
    match timeframe.lower():
        case "7d":
            return timedelta(days=7)
        case "14d":
            return timedelta(days=14)
        case "30d":
            return timedelta(days=30)
        case "90d":
            return timedelta(days=90)
        case "1y" | "365d":
            return timedelta(days=365)
        case _:
            # Try numeric prefix
            import re
            m = re.match(r"^(\d+)([dmy])$", timeframe.lower())
            if m:
                n, unit = int(m.group(1)), m.group(2)
                if unit == "d":
                    return timedelta(days=n)
                if unit == "m":
                    return timedelta(days=n * 30)
                if unit == "y":
                    return timedelta(days=n * 365)
    raise ValueError(f"Unsupported timeframe: {timeframe!r}")


# ---------------------------------------------------------------------------
# TrendEngine
# ---------------------------------------------------------------------------


class TrendEngine:
    """
    Compute market intelligence trends from the Talentora job database.

    All methods accept a ``timeframe`` string (``"7d"``, ``"30d"``, etc.)
    and optional region filters, and return structured dataclass objects.
    """

    def compute_skill_trends(
        self,
        timeframe: str = "30d",
        region: str | None = None,
    ) -> list[SkillTrend]:
        """
        Compute demand counts and growth rates for all tracked skills.

        Parameters
        ----------
        timeframe:
            Rolling window string.
        region:
            Optional ISO 3166-1 / NUTS region code to filter jobs.

        Returns
        -------
        List of :class:`SkillTrend` sorted by ``demand_count`` descending.
        """
        log.info("trend_engine.compute_skill_trends", timeframe=timeframe, region=region)
        delta = _parse_timeframe(timeframe)
        cutoff = datetime.now(timezone.utc) - delta
        prev_cutoff = cutoff - delta

        try:
            from services.ingestion.pipeline import JobRepository

            repo = JobRepository()
            current_counts = repo.count_skills_since(cutoff, region=region)
            prev_counts = repo.count_skills_between(prev_cutoff, cutoff, region=region)
            salary_map = repo.avg_salary_by_skill(cutoff, region=region)

            trends: list[SkillTrend] = []
            for skill, count in current_counts.items():
                prev = prev_counts.get(skill, 0)
                growth = (count - prev) / max(prev, 1)
                trends.append(
                    SkillTrend(
                        skill_name=skill,
                        demand_count=count,
                        growth_rate=round(growth, 4),
                        avg_salary=salary_map.get(skill),
                        region=region,
                        timeframe=timeframe,
                    )
                )

            trends.sort(key=lambda t: t.demand_count, reverse=True)
            log.info("trend_engine.skill_trends_done", count=len(trends))
            return trends

        except Exception as exc:
            log.error("trend_engine.compute_skill_trends.error", error=str(exc))
            return []

    def compute_salary_trends(self, role: str, region: str = "FR") -> SalaryTrend | None:
        """
        Compute salary percentiles for a canonical role in a region.

        Parameters
        ----------
        role:
            Canonical role identifier (e.g. ``"software_engineer"``).
        region:
            ISO 3166-1 alpha-2 or NUTS region code.

        Returns
        -------
        :class:`SalaryTrend` or ``None`` if insufficient data.
        """
        log.info("trend_engine.compute_salary_trends", role=role, region=region)
        try:
            from services.ingestion.pipeline import JobRepository

            repo = JobRepository()
            stats = repo.salary_percentiles(role=role, region=region)
            if not stats:
                return None

            return SalaryTrend(
                role=role,
                region=region,
                median_salary=stats.get("p50"),
                p25_salary=stats.get("p25"),
                p75_salary=stats.get("p75"),
                sample_count=stats.get("count", 0),
                timeframe="all_time",
            )
        except Exception as exc:
            log.error("trend_engine.compute_salary_trends.error", error=str(exc))
            return None

    def compute_demand_by_region(
        self, skill: str, timeframe: str = "30d"
    ) -> RegionDemand:
        """
        Count job demand for a skill broken down by region.

        Parameters
        ----------
        skill:
            Canonical skill name (e.g. ``"python"``).
        timeframe:
            Rolling window string.

        Returns
        -------
        :class:`RegionDemand` mapping region codes to job counts.
        """
        log.info("trend_engine.compute_demand_by_region", skill=skill, timeframe=timeframe)
        delta = _parse_timeframe(timeframe)
        cutoff = datetime.now(timezone.utc) - delta

        try:
            from services.ingestion.pipeline import JobRepository

            repo = JobRepository()
            region_counts = repo.count_skill_by_region(skill=skill, since=cutoff)
            return RegionDemand(skill=skill, regions=region_counts, timeframe=timeframe)
        except Exception as exc:
            log.error("trend_engine.compute_demand_by_region.error", error=str(exc))
            return RegionDemand(skill=skill, regions={}, timeframe=timeframe)

    def detect_emerging_skills(
        self,
        timeframe: str = "30d",
        threshold: float = 0.20,
    ) -> list[EmergingSkill]:
        """
        Identify skills whose demand grew faster than ``threshold`` over ``timeframe``.

        Parameters
        ----------
        timeframe:
            Rolling window string.
        threshold:
            Minimum relative growth rate (0.20 = 20 %).

        Returns
        -------
        List of :class:`EmergingSkill` sorted by growth rate descending.
        """
        log.info("trend_engine.detect_emerging_skills", timeframe=timeframe, threshold=threshold)
        trends = self.compute_skill_trends(timeframe=timeframe)
        emerging = [
            EmergingSkill(
                skill_name=t.skill_name,
                growth_rate=t.growth_rate,
                absolute_count=t.demand_count,
                first_seen=None,
                timeframe=timeframe,
            )
            for t in trends
            if t.growth_rate >= threshold and t.demand_count >= 5
        ]
        emerging.sort(key=lambda s: s.growth_rate, reverse=True)
        log.info("trend_engine.emerging_skills_found", count=len(emerging))
        return emerging

    def compute_remote_trends(self, timeframe: str = "30d") -> RemoteTrend | None:
        """
        Compute the proportion of remote, partial-remote, and on-site offers.

        Parameters
        ----------
        timeframe:
            Rolling window string.

        Returns
        -------
        :class:`RemoteTrend` or ``None`` if no data.
        """
        log.info("trend_engine.compute_remote_trends", timeframe=timeframe)
        delta = _parse_timeframe(timeframe)
        cutoff = datetime.now(timezone.utc) - delta

        try:
            from services.ingestion.pipeline import JobRepository

            repo = JobRepository()
            counts = repo.count_by_remote_type(since=cutoff)
            total = sum(counts.values())
            if total == 0:
                return None

            return RemoteTrend(
                remote_percentage=round(counts.get("full", 0) / total * 100, 2),
                partial_percentage=round(counts.get("partial", 0) / total * 100, 2),
                onsite_percentage=round(counts.get("none", 0) / total * 100, 2),
                timeframe=timeframe,
                sample_count=total,
            )
        except Exception as exc:
            log.error("trend_engine.compute_remote_trends.error", error=str(exc))
            return None
