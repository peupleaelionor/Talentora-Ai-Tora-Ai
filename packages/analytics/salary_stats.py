"""
Salary statistics computation for the Talentora analytics package.

Provides percentile-based salary analysis aggregated by role, region,
contract type, and time window.
"""

from __future__ import annotations

import statistics
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any

import structlog

log = structlog.get_logger(__name__)


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------


@dataclass
class SalaryDistribution:
    """Salary distribution stats for a cohort of job offers."""

    role: str | None
    region: str | None
    contract_type: str | None
    currency: str
    period: str  # "yearly" | "monthly" | "daily" | "hourly"
    sample_count: int
    mean: float | None
    median: float | None
    p10: float | None
    p25: float | None
    p75: float | None
    p90: float | None
    std_dev: float | None
    timeframe: str
    computed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict[str, Any]:
        return {
            "role": self.role,
            "region": self.region,
            "contract_type": self.contract_type,
            "currency": self.currency,
            "period": self.period,
            "sample_count": self.sample_count,
            "mean": self.mean,
            "median": self.median,
            "p10": self.p10,
            "p25": self.p25,
            "p75": self.p75,
            "p90": self.p90,
            "std_dev": self.std_dev,
            "timeframe": self.timeframe,
            "computed_at": self.computed_at.isoformat(),
        }


# ---------------------------------------------------------------------------
# Stats helpers
# ---------------------------------------------------------------------------


def _percentile(data: list[float], p: float) -> float | None:
    """Compute the p-th percentile (0–100) of a sorted list."""
    if not data:
        return None
    sorted_data = sorted(data)
    n = len(sorted_data)
    idx = (p / 100) * (n - 1)
    lo, hi = int(idx), min(int(idx) + 1, n - 1)
    frac = idx - lo
    return round(sorted_data[lo] + frac * (sorted_data[hi] - sorted_data[lo]), 2)


def _compute_stats(values: list[float]) -> dict[str, float | None]:
    if not values:
        return {k: None for k in ("mean", "median", "p10", "p25", "p75", "p90", "std_dev")}
    return {
        "mean": round(statistics.mean(values), 2),
        "median": round(statistics.median(values), 2),
        "p10": _percentile(values, 10),
        "p25": _percentile(values, 25),
        "p75": _percentile(values, 75),
        "p90": _percentile(values, 90),
        "std_dev": round(statistics.stdev(values), 2) if len(values) > 1 else 0.0,
    }


# ---------------------------------------------------------------------------
# SalaryStats
# ---------------------------------------------------------------------------


class SalaryStats:
    """
    Compute salary distribution statistics from the job database.

    All methods query the ``normalized_jobs`` table for offers that have
    both ``salary_min`` and ``salary_max`` populated.
    """

    def compute(
        self,
        timeframe: str = "30d",
        role: str | None = None,
        region: str | None = None,
        contract_type: str | None = None,
        currency: str = "EUR",
        period: str = "yearly",
    ) -> dict[str, Any]:
        """
        Compute salary distribution for the given filters.

        Parameters
        ----------
        timeframe:
            Rolling window (``"7d"``, ``"30d"``, ``"90d"``).
        role:
            Canonical role filter.
        region:
            ISO 3166-1 / NUTS region filter.
        contract_type:
            Contract type filter (``"CDI"``, ``"CDD"``, etc.).
        currency:
            ISO 4217 currency (default ``"EUR"``).
        period:
            Salary normalisation period (default ``"yearly"``).

        Returns
        -------
        Serialised :class:`SalaryDistribution` dict.
        """
        log.info(
            "salary_stats.compute",
            timeframe=timeframe,
            role=role,
            region=region,
        )
        delta = self._parse_timeframe(timeframe)
        cutoff = datetime.now(timezone.utc) - delta

        try:
            salaries = self._fetch_salaries(
                since=cutoff,
                role=role,
                region=region,
                contract_type=contract_type,
                currency=currency,
                period=period,
            )
            stats = _compute_stats(salaries)
            dist = SalaryDistribution(
                role=role,
                region=region,
                contract_type=contract_type,
                currency=currency,
                period=period,
                sample_count=len(salaries),
                timeframe=timeframe,
                **stats,
            )
            return dist.to_dict()

        except Exception as exc:
            log.error("salary_stats.compute.error", error=str(exc))
            return {}

    # ------------------------------------------------------------------
    # Breakdown helpers
    # ------------------------------------------------------------------

    def by_role(
        self, timeframe: str = "30d", region: str | None = None
    ) -> list[dict[str, Any]]:
        """
        Return salary distributions broken down by canonical role.

        Parameters
        ----------
        timeframe:
            Rolling window.
        region:
            Optional region filter.

        Returns
        -------
        List of serialised :class:`SalaryDistribution` dicts.
        """
        log.info("salary_stats.by_role", timeframe=timeframe)
        try:
            from packages.nlp.job_classifier import ROLE_TAXONOMY

            return [
                self.compute(timeframe=timeframe, role=role, region=region)
                for role in ROLE_TAXONOMY
            ]
        except Exception as exc:
            log.error("salary_stats.by_role.error", error=str(exc))
            return []

    def by_region(
        self, timeframe: str = "30d", role: str | None = None
    ) -> list[dict[str, Any]]:
        """
        Return salary distributions broken down by country.

        Parameters
        ----------
        timeframe:
            Rolling window.
        role:
            Optional canonical role filter.

        Returns
        -------
        List of serialised :class:`SalaryDistribution` dicts.
        """
        log.info("salary_stats.by_region", timeframe=timeframe)
        try:
            from services.ingestion.pipeline import JobRepository

            repo = JobRepository()
            regions = repo.list_active_regions()
            return [
                self.compute(timeframe=timeframe, region=r, role=role)
                for r in regions
            ]
        except Exception as exc:
            log.error("salary_stats.by_region.error", error=str(exc))
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

    @staticmethod
    def _fetch_salaries(
        since: datetime,
        role: str | None,
        region: str | None,
        contract_type: str | None,
        currency: str,
        period: str,
    ) -> list[float]:
        """Retrieve midpoint salary values from the database."""
        try:
            from services.ingestion.pipeline import JobRepository

            repo = JobRepository()
            return repo.get_salary_values(
                since=since,
                role=role,
                region=region,
                contract_type=contract_type,
                currency=currency,
                period=period,
            )
        except Exception:
            return []
