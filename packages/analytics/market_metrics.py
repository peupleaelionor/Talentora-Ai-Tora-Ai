"""
Market health metrics for the Talentora analytics package.

Aggregates supply/demand balance, time-to-fill proxies, job velocity
(new listings per day), saturation indices, and competition rates by
role and region.
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
class MarketHealthSnapshot:
    """Point-in-time market health metrics for a cohort."""

    region: str | None
    role: str | None
    timeframe: str
    total_listings: int
    new_listings: int  # added in the timeframe
    velocity: float  # new listings per day
    avg_listing_age_days: float | None
    supply_demand_ratio: float | None  # <1 = more demand than supply (seller's market)
    competition_index: float | None  # average number of jobs per unique skill
    remote_share: float  # fraction of remote/hybrid offers
    contract_distribution: dict[str, float]  # contract_type -> share
    computed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict[str, Any]:
        return {
            "region": self.region,
            "role": self.role,
            "timeframe": self.timeframe,
            "total_listings": self.total_listings,
            "new_listings": self.new_listings,
            "velocity": round(self.velocity, 2),
            "avg_listing_age_days": self.avg_listing_age_days,
            "supply_demand_ratio": self.supply_demand_ratio,
            "competition_index": self.competition_index,
            "remote_share": round(self.remote_share, 4),
            "contract_distribution": self.contract_distribution,
            "computed_at": self.computed_at.isoformat(),
        }


# ---------------------------------------------------------------------------
# MarketMetrics
# ---------------------------------------------------------------------------


class MarketMetrics:
    """
    Compute market health and velocity metrics from the job database.
    """

    def compute(
        self,
        timeframe: str = "30d",
        region: str | None = None,
        role: str | None = None,
    ) -> dict[str, Any]:
        """
        Compute a market health snapshot.

        Parameters
        ----------
        timeframe:
            Rolling window (``"7d"``, ``"30d"``, ``"90d"``).
        region:
            ISO 3166-1 / NUTS region filter.
        role:
            Canonical role filter.

        Returns
        -------
        Serialised :class:`MarketHealthSnapshot` dict.
        """
        log.info("market_metrics.compute", timeframe=timeframe, region=region, role=role)
        delta = self._parse_timeframe(timeframe)
        now = datetime.now(timezone.utc)
        cutoff = now - delta

        try:
            from services.ingestion.pipeline import JobRepository

            repo = JobRepository()

            total = repo.count_jobs(since=cutoff, region=region, role=role)
            new_count = repo.count_new_jobs(since=cutoff, region=region, role=role)
            days = max(delta.days, 1)
            velocity = new_count / days

            avg_age = repo.avg_listing_age_days(since=cutoff, region=region, role=role)
            remote_counts = repo.count_by_remote_type(since=cutoff, region=region, role=role)
            contract_counts = repo.count_by_contract_type(since=cutoff, region=region, role=role)

            total_contracts = sum(contract_counts.values()) or 1
            contract_dist = {k: round(v / total_contracts, 4) for k, v in contract_counts.items()}

            remote_total = sum(remote_counts.values()) or 1
            remote_share = (
                remote_counts.get("full", 0) + remote_counts.get("partial", 0)
            ) / remote_total

            snapshot = MarketHealthSnapshot(
                region=region,
                role=role,
                timeframe=timeframe,
                total_listings=total,
                new_listings=new_count,
                velocity=velocity,
                avg_listing_age_days=avg_age,
                supply_demand_ratio=None,  # requires external labour supply data
                competition_index=None,    # set via compute_competition_index
                remote_share=remote_share,
                contract_distribution=contract_dist,
            )
            log.info(
                "market_metrics.done",
                total=total,
                velocity=round(velocity, 2),
                region=region,
            )
            return snapshot.to_dict()

        except Exception as exc:
            log.error("market_metrics.compute.error", error=str(exc))
            return {}

    def compute_competition_index(
        self,
        skill: str,
        timeframe: str = "30d",
        region: str | None = None,
    ) -> float | None:
        """
        Estimate competition for a skill as the average number of jobs per
        unique job seeker proxy.

        This is computed as:
            ``jobs_requiring_skill / total_jobs_in_period``

        Higher values indicate that the skill is more broadly demanded.

        Parameters
        ----------
        skill:
            Canonical skill name.
        timeframe:
            Rolling window.
        region:
            Optional region filter.

        Returns
        -------
        Competition index float, or ``None`` if data unavailable.
        """
        log.info("market_metrics.competition_index", skill=skill, timeframe=timeframe)
        delta = self._parse_timeframe(timeframe)
        cutoff = datetime.now(timezone.utc) - delta

        try:
            from services.ingestion.pipeline import JobRepository

            repo = JobRepository()
            skill_jobs = repo.count_jobs_with_skill(skill=skill, since=cutoff, region=region)
            total = repo.count_jobs(since=cutoff, region=region)
            if total == 0:
                return None
            return round(skill_jobs / total, 4)
        except Exception as exc:
            log.error("market_metrics.competition_index.error", error=str(exc))
            return None

    def top_hiring_companies(
        self,
        timeframe: str = "30d",
        region: str | None = None,
        top_n: int = 20,
    ) -> list[dict[str, Any]]:
        """
        Return the companies with the most active listings in the period.

        Parameters
        ----------
        timeframe:
            Rolling window.
        region:
            Optional region filter.
        top_n:
            Maximum number of companies to return.

        Returns
        -------
        List of dicts with ``company`` and ``listing_count`` keys.
        """
        log.info("market_metrics.top_hiring_companies", timeframe=timeframe)
        delta = self._parse_timeframe(timeframe)
        cutoff = datetime.now(timezone.utc) - delta

        try:
            from services.ingestion.pipeline import JobRepository

            repo = JobRepository()
            return repo.top_companies_by_listings(since=cutoff, region=region, limit=top_n)
        except Exception as exc:
            log.error("market_metrics.top_companies.error", error=str(exc))
            return []

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _parse_timeframe(timeframe: str) -> timedelta:
        mapping = {"7d": 7, "14d": 14, "30d": 30, "90d": 90, "1y": 365, "365d": 365}
        days = mapping.get(timeframe.lower())
        if days is None:
            raise ValueError(f"Unsupported timeframe: {timeframe!r}")
        return timedelta(days=days)
