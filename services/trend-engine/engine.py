"""
Trend computation service for Talentora.

Wraps :class:`~packages.analytics.trend_engine.TrendEngine` with
persistence logic: computed snapshots are stored in the database so
dashboards can query pre-aggregated results without re-running heavy
analytics queries on every request.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import structlog

from packages.analytics.trend_engine import (
    TrendEngine,
    SkillTrend,
    SalaryTrend,
    RegionDemand,
    EmergingSkill,
    RemoteTrend,
)

log = structlog.get_logger(__name__)

# Supported timeframe strings for scheduled runs
SCHEDULED_TIMEFRAMES = ["7d", "30d", "90d"]


class TrendComputationService:
    """
    Compute and persist trend snapshots.

    Intended to be called from the Celery ``compute_trends`` beat task.
    """

    def __init__(self) -> None:
        self._engine = TrendEngine()

    # ------------------------------------------------------------------
    # Full snapshot run
    # ------------------------------------------------------------------

    def run_full(
        self,
        timeframe: str = "30d",
        region: str | None = None,
    ) -> dict[str, Any]:
        """
        Compute and persist all trend categories for a single timeframe.

        Parameters
        ----------
        timeframe:
            Rolling window string.
        region:
            Optional region filter.

        Returns
        -------
        Summary dict with counts of persisted trend records.
        """
        log.info("trend_service.run_full.start", timeframe=timeframe, region=region)
        summary: dict[str, Any] = {"timeframe": timeframe, "region": region}

        skill_trends = self._engine.compute_skill_trends(timeframe=timeframe, region=region)
        self._persist_skill_trends(skill_trends, timeframe=timeframe, region=region)
        summary["skill_trends"] = len(skill_trends)

        emerging = self._engine.detect_emerging_skills(timeframe=timeframe)
        self._persist_emerging_skills(emerging, timeframe=timeframe)
        summary["emerging_skills"] = len(emerging)

        remote = self._engine.compute_remote_trends(timeframe=timeframe)
        if remote:
            self._persist_remote_trend(remote)
        summary["remote_trend_computed"] = remote is not None

        log.info("trend_service.run_full.done", **summary)
        return summary

    def run_all_timeframes(self, region: str | None = None) -> list[dict[str, Any]]:
        """
        Run the full snapshot for every scheduled timeframe.

        Parameters
        ----------
        region:
            Optional region filter.

        Returns
        -------
        List of summary dicts, one per timeframe.
        """
        results = []
        for tf in SCHEDULED_TIMEFRAMES:
            try:
                results.append(self.run_full(timeframe=tf, region=region))
            except Exception as exc:
                log.error("trend_service.timeframe_failed", timeframe=tf, error=str(exc))
        return results

    # ------------------------------------------------------------------
    # Persistence helpers
    # ------------------------------------------------------------------

    def _persist_skill_trends(
        self,
        trends: list[SkillTrend],
        timeframe: str,
        region: str | None,
    ) -> None:
        if not trends:
            return
        try:
            from services.ingestion.pipeline import JobRepository

            repo = JobRepository()
            repo.upsert_skill_trends(
                [
                    {
                        "skill_name": t.skill_name,
                        "demand_count": t.demand_count,
                        "growth_rate": t.growth_rate,
                        "avg_salary": t.avg_salary,
                        "region": region,
                        "timeframe": timeframe,
                        "computed_at": t.computed_at.isoformat(),
                    }
                    for t in trends
                ]
            )
        except Exception as exc:
            log.error("trend_service.persist_skill_trends.error", error=str(exc))

    def _persist_emerging_skills(
        self, skills: list[EmergingSkill], timeframe: str
    ) -> None:
        if not skills:
            return
        try:
            from services.ingestion.pipeline import JobRepository

            repo = JobRepository()
            repo.upsert_emerging_skills(
                [
                    {
                        "skill_name": s.skill_name,
                        "growth_rate": s.growth_rate,
                        "absolute_count": s.absolute_count,
                        "timeframe": timeframe,
                        "computed_at": s.computed_at.isoformat(),
                    }
                    for s in skills
                ]
            )
        except Exception as exc:
            log.error("trend_service.persist_emerging.error", error=str(exc))

    def _persist_remote_trend(self, remote: RemoteTrend) -> None:
        try:
            from services.ingestion.pipeline import JobRepository

            repo = JobRepository()
            repo.upsert_remote_trend(
                {
                    "remote_percentage": remote.remote_percentage,
                    "partial_percentage": remote.partial_percentage,
                    "onsite_percentage": remote.onsite_percentage,
                    "sample_count": remote.sample_count,
                    "timeframe": remote.timeframe,
                    "computed_at": remote.computed_at.isoformat(),
                }
            )
        except Exception as exc:
            log.error("trend_service.persist_remote.error", error=str(exc))
