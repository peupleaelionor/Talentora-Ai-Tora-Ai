"""
Report generation Celery tasks for the Talentora worker.

Builds scheduled and on-demand market intelligence reports that are
stored in S3 and optionally emailed to subscribers.
"""

from __future__ import annotations

from typing import Any

import structlog

from worker.celery_app import app

log = structlog.get_logger(__name__)


# ---------------------------------------------------------------------------
# Task: generate_salary_report
# ---------------------------------------------------------------------------


@app.task(
    bind=True,
    name="worker.tasks.reporting.generate_salary_report",
    max_retries=2,
    default_retry_delay=60,
    acks_late=True,
    track_started=True,
    time_limit=1800,
)
def generate_salary_report(
    self,
    region: str | None = None,
    role: str | None = None,
    timeframe: str = "30d",
) -> dict[str, Any]:
    """
    Generate a salary statistics report and upload it to S3.

    Parameters
    ----------
    region:
        Optional ISO 3166-1 / NUTS region filter.
    role:
        Optional canonical role filter (e.g. ``"software_engineer"``).
    timeframe:
        Rolling window: ``"7d"``, ``"30d"``, ``"90d"``.

    Returns
    -------
    dict with ``report_id``, ``s3_key``, and high-level ``stats``.
    """
    logger = log.bind(region=region, role=role, timeframe=timeframe)
    logger.info("salary_report.start")

    try:
        import uuid
        from packages.analytics.salary_stats import SalaryStats
        from services.reporting.storage import ReportStorage

        stats_engine = SalaryStats()
        stats = stats_engine.compute(timeframe=timeframe, region=region, role=role)

        report_id = str(uuid.uuid4())
        storage = ReportStorage()
        s3_key = storage.upload_json(
            data=stats,
            prefix="salary-reports",
            report_id=report_id,
        )

        logger.info("salary_report.complete", report_id=report_id, s3_key=s3_key)
        return {"report_id": report_id, "s3_key": s3_key, "stats": stats}

    except Exception as exc:
        logger.warning("salary_report.retry", error=str(exc))
        try:
            raise self.retry(exc=exc, countdown=60)
        except Exception:
            logger.error("salary_report.failed", error=str(exc))
            raise


# ---------------------------------------------------------------------------
# Task: generate_market_health_report
# ---------------------------------------------------------------------------


@app.task(
    bind=True,
    name="worker.tasks.reporting.generate_market_health_report",
    max_retries=2,
    default_retry_delay=60,
    acks_late=True,
    track_started=True,
    time_limit=1800,
)
def generate_market_health_report(
    self,
    region: str | None = None,
    timeframe: str = "30d",
) -> dict[str, Any]:
    """
    Generate a market health report covering demand, supply, and velocity.

    Parameters
    ----------
    region:
        Optional NUTS region filter.
    timeframe:
        Rolling window string.

    Returns
    -------
    dict with ``report_id``, ``s3_key``, and aggregated ``metrics``.
    """
    logger = log.bind(region=region, timeframe=timeframe)
    logger.info("market_health_report.start")

    try:
        import uuid
        from packages.analytics.market_metrics import MarketMetrics
        from services.reporting.storage import ReportStorage

        engine = MarketMetrics()
        metrics = engine.compute(timeframe=timeframe, region=region)

        report_id = str(uuid.uuid4())
        storage = ReportStorage()
        s3_key = storage.upload_json(
            data=metrics,
            prefix="market-health",
            report_id=report_id,
        )

        logger.info("market_health_report.complete", report_id=report_id)
        return {"report_id": report_id, "s3_key": s3_key, "metrics": metrics}

    except Exception as exc:
        logger.warning("market_health_report.retry", error=str(exc))
        try:
            raise self.retry(exc=exc, countdown=60)
        except Exception:
            logger.error("market_health_report.failed", error=str(exc))
            raise


# ---------------------------------------------------------------------------
# Task: generate_skills_demand_report
# ---------------------------------------------------------------------------


@app.task(
    bind=True,
    name="worker.tasks.reporting.generate_skills_demand_report",
    max_retries=2,
    default_retry_delay=60,
    acks_late=True,
    track_started=True,
    time_limit=1800,
)
def generate_skills_demand_report(
    self,
    timeframe: str = "30d",
    region: str | None = None,
    top_n: int = 50,
) -> dict[str, Any]:
    """
    Generate a ranked skills demand report.

    Parameters
    ----------
    timeframe:
        Rolling window string.
    region:
        Optional region filter.
    top_n:
        Number of top skills to include.

    Returns
    -------
    dict with ``report_id``, ``s3_key``, and list of top ``skills``.
    """
    logger = log.bind(timeframe=timeframe, region=region, top_n=top_n)
    logger.info("skills_demand_report.start")

    try:
        import uuid
        from packages.analytics.trend_engine import TrendEngine
        from services.reporting.storage import ReportStorage

        engine = TrendEngine()
        skill_trends = engine.compute_skill_trends(timeframe=timeframe, region=region)

        top_skills = sorted(skill_trends, key=lambda s: s.demand_count, reverse=True)[:top_n]
        data = [
            {
                "skill": t.skill_name,
                "demand_count": t.demand_count,
                "growth_rate": t.growth_rate,
                "avg_salary": t.avg_salary,
            }
            for t in top_skills
        ]

        report_id = str(uuid.uuid4())
        storage = ReportStorage()
        s3_key = storage.upload_json(
            data={"timeframe": timeframe, "region": region, "skills": data},
            prefix="skills-demand",
            report_id=report_id,
        )

        logger.info("skills_demand_report.complete", report_id=report_id, skills_count=len(data))
        return {"report_id": report_id, "s3_key": s3_key, "skills": data}

    except Exception as exc:
        logger.warning("skills_demand_report.retry", error=str(exc))
        try:
            raise self.retry(exc=exc, countdown=60)
        except Exception:
            logger.error("skills_demand_report.failed", error=str(exc))
            raise
