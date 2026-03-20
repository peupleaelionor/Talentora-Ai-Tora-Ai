"""
Celery ingestion tasks for the Talentora worker.

Orchestrates fetching raw jobs from external sources, persisting them,
and dispatching downstream processing tasks.
"""

from __future__ import annotations

import uuid
from typing import Any

import structlog
from celery import group, shared_task
from celery.exceptions import MaxRetriesExceededError
from tenacity import RetryError

from worker.celery_app import app

log = structlog.get_logger(__name__)

# ---------------------------------------------------------------------------
# Task: run_ingestion_pipeline
# ---------------------------------------------------------------------------


@app.task(
    bind=True,
    name="worker.tasks.ingestion.run_ingestion_pipeline",
    max_retries=3,
    default_retry_delay=60,
    acks_late=True,
    track_started=True,
)
def run_ingestion_pipeline(
    self,
    source_id: str,
    options: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Run the full ingestion pipeline for a single source.

    Parameters
    ----------
    source_id:
        Registry key identifying the connector to use.
    options:
        Optional overrides forwarded to the connector (filters, page
        range, incremental flag, etc.).

    Returns
    -------
    dict with ``source_id``, ``fetched``, ``queued``, and ``pipeline_id``.
    """
    options = options or {}
    pipeline_id = str(uuid.uuid4())
    logger = log.bind(source_id=source_id, pipeline_id=pipeline_id)

    logger.info("ingestion_pipeline.start", options=options)

    try:
        from services.ingestion.pipeline import IngestionPipeline

        pipeline = IngestionPipeline(source_id=source_id, pipeline_id=pipeline_id)
        incremental: bool = options.get("incremental", False)

        if incremental:
            result = pipeline.run_incremental(**options)
        else:
            result = pipeline.run(**options)

        logger.info("ingestion_pipeline.complete", result=result)
        return {"source_id": source_id, "pipeline_id": pipeline_id, **result}

    except Exception as exc:
        logger.error("ingestion_pipeline.error", error=str(exc), exc_info=True)
        try:
            raise self.retry(exc=exc, countdown=60 * (self.request.retries + 1))
        except MaxRetriesExceededError:
            logger.critical("ingestion_pipeline.max_retries_exceeded", source_id=source_id)
            raise


# ---------------------------------------------------------------------------
# Task: fetch_jobs_from_source
# ---------------------------------------------------------------------------


@app.task(
    bind=True,
    name="worker.tasks.ingestion.fetch_jobs_from_source",
    max_retries=5,
    default_retry_delay=30,
    rate_limit="10/m",
    acks_late=True,
)
def fetch_jobs_from_source(
    self,
    source_id: str,
    page: int = 1,
    filters: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Fetch a single page of job listings from a source connector.

    Dispatches a ``process_raw_job`` task for each raw job retrieved.

    Parameters
    ----------
    source_id:
        Connector registry key.
    page:
        Page number to fetch (1-indexed).
    filters:
        Optional query filters passed to ``connector.fetch_job_list``.

    Returns
    -------
    dict with ``source_id``, ``page``, ``count``, and list of ``raw_job_ids``.
    """
    filters = filters or {}
    logger = log.bind(source_id=source_id, page=page)

    logger.info("fetch_jobs.start")

    try:
        import asyncio
        from packages.connectors.registry import ConnectorRegistry

        connector = ConnectorRegistry.get(source_id)
        raw_jobs = asyncio.get_event_loop().run_until_complete(
            connector.fetch_job_list(page=page, filters=filters)
        )

        raw_job_ids: list[str] = []
        for raw_job in raw_jobs:
            stored_id = asyncio.get_event_loop().run_until_complete(
                connector.store_raw(raw_job)
            )
            raw_job_ids.append(stored_id)
            process_raw_job.delay(stored_id)

        logger.info("fetch_jobs.complete", count=len(raw_job_ids))
        return {"source_id": source_id, "page": page, "count": len(raw_job_ids), "raw_job_ids": raw_job_ids}

    except Exception as exc:
        logger.warning("fetch_jobs.retry", error=str(exc), retries=self.request.retries)
        try:
            raise self.retry(exc=exc, countdown=30 * (2 ** self.request.retries))
        except MaxRetriesExceededError:
            logger.error("fetch_jobs.max_retries_exceeded", source_id=source_id, page=page)
            raise


# ---------------------------------------------------------------------------
# Task: process_raw_job
# ---------------------------------------------------------------------------


@app.task(
    bind=True,
    name="worker.tasks.ingestion.process_raw_job",
    max_retries=3,
    default_retry_delay=10,
    rate_limit="60/m",
    acks_late=True,
)
def process_raw_job(self, raw_job_id: str) -> dict[str, Any]:
    """
    Process a single raw job record through the normalization pipeline.

    Dispatches ``normalize_job_offer`` and, on success,
    ``extract_skills_from_job``.

    Parameters
    ----------
    raw_job_id:
        UUID of the persisted raw job record.

    Returns
    -------
    dict with ``raw_job_id`` and downstream ``job_id``.
    """
    logger = log.bind(raw_job_id=raw_job_id)
    logger.info("process_raw_job.start")

    try:
        from worker.tasks.normalization import normalize_job_offer

        result = normalize_job_offer.delay(raw_job_id)
        job_id = result.get(timeout=120)

        if job_id:
            from worker.tasks.analysis import extract_skills_from_job, generate_embeddings

            extract_skills_from_job.delay(job_id)
            generate_embeddings.delay(job_id)
            logger.info("process_raw_job.complete", job_id=job_id)

        return {"raw_job_id": raw_job_id, "job_id": job_id}

    except Exception as exc:
        logger.warning("process_raw_job.retry", error=str(exc))
        try:
            raise self.retry(exc=exc, countdown=10 * (self.request.retries + 1))
        except MaxRetriesExceededError:
            logger.error("process_raw_job.dead_letter", raw_job_id=raw_job_id)
            _send_to_dead_letter_queue(raw_job_id, str(exc))
            raise


# ---------------------------------------------------------------------------
# Task: run_all_sources
# ---------------------------------------------------------------------------


@app.task(
    name="worker.tasks.ingestion.run_all_sources",
    acks_late=True,
    track_started=True,
)
def run_all_sources(incremental: bool = False) -> dict[str, Any]:
    """
    Dispatch ingestion pipelines for every registered source connector.

    Parameters
    ----------
    incremental:
        When ``True``, each pipeline runs in incremental mode (fetches
        only new/updated records since the last run).

    Returns
    -------
    dict with ``dispatched`` count and list of ``source_ids``.
    """
    logger = log.bind(incremental=incremental)
    logger.info("run_all_sources.start")

    try:
        from packages.connectors.registry import ConnectorRegistry

        source_ids = ConnectorRegistry.list_sources()

        jobs = group(
            run_ingestion_pipeline.s(sid, {"incremental": incremental})
            for sid in source_ids
        )
        jobs.apply_async()

        logger.info("run_all_sources.dispatched", count=len(source_ids), sources=source_ids)
        return {"dispatched": len(source_ids), "source_ids": source_ids}

    except Exception as exc:
        logger.error("run_all_sources.error", error=str(exc), exc_info=True)
        raise


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _send_to_dead_letter_queue(raw_job_id: str, reason: str) -> None:
    """Persist failed raw job ID to the dead-letter queue for manual review."""
    try:
        import json
        import redis
        import os

        r = redis.from_url(os.environ.get("REDIS_URL", "redis://localhost:6379/0"))
        payload = json.dumps({"raw_job_id": raw_job_id, "reason": reason})
        r.lpush("talentora:dlq:ingestion", payload)
        log.warning("dead_letter_queue.pushed", raw_job_id=raw_job_id)
    except Exception as exc:
        log.error("dead_letter_queue.push_failed", raw_job_id=raw_job_id, error=str(exc))
