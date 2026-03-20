"""
Main ingestion pipeline orchestrator for Talentora.

The ``IngestionPipeline`` class drives a source connector through the
full fetch → deduplicate → normalize → enrich → index lifecycle with
per-stage error handling, progress tracking, and dead-letter queue
support.

``JobRepository`` provides a thin database abstraction used by the
pipeline and by analytics/trend modules.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

import structlog

log = structlog.get_logger(__name__)


# ---------------------------------------------------------------------------
# Pipeline metrics / progress
# ---------------------------------------------------------------------------


@dataclass
class PipelineMetrics:
    """Counters for a single pipeline run."""

    source_id: str
    pipeline_id: str
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    finished_at: datetime | None = None
    pages_fetched: int = 0
    raw_jobs_fetched: int = 0
    duplicates_skipped: int = 0
    normalized: int = 0
    enriched: int = 0
    indexed: int = 0
    errors: int = 0
    dead_lettered: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_id": self.source_id,
            "pipeline_id": self.pipeline_id,
            "started_at": self.started_at.isoformat(),
            "finished_at": self.finished_at.isoformat() if self.finished_at else None,
            "pages_fetched": self.pages_fetched,
            "raw_jobs_fetched": self.raw_jobs_fetched,
            "duplicates_skipped": self.duplicates_skipped,
            "normalized": self.normalized,
            "enriched": self.enriched,
            "indexed": self.indexed,
            "errors": self.errors,
            "dead_lettered": self.dead_lettered,
        }


# ---------------------------------------------------------------------------
# IngestionPipeline
# ---------------------------------------------------------------------------


class IngestionPipeline:
    """
    Orchestrate the end-to-end ingestion of job offers from a single source.

    Parameters
    ----------
    source_id:
        Registry key identifying the connector to use.
    pipeline_id:
        Optional UUID for tracking; auto-generated when omitted.
    """

    def __init__(
        self,
        source_id: str,
        pipeline_id: str | None = None,
    ) -> None:
        self.source_id = source_id
        self.pipeline_id = pipeline_id or str(uuid.uuid4())
        self._metrics = PipelineMetrics(
            source_id=source_id,
            pipeline_id=self.pipeline_id,
        )

    # ------------------------------------------------------------------
    # Public run modes
    # ------------------------------------------------------------------

    def run(
        self,
        filters: dict[str, Any] | None = None,
        max_pages: int = 100,
        **_: Any,
    ) -> dict[str, Any]:
        """
        Run a full ingestion pass (all pages).

        Parameters
        ----------
        filters:
            Optional source-specific query parameters.
        max_pages:
            Safety limit on the number of pages to fetch.

        Returns
        -------
        Serialised :class:`PipelineMetrics` dict.
        """
        import asyncio

        log.info("pipeline.run.start", source_id=self.source_id, pipeline_id=self.pipeline_id)
        asyncio.get_event_loop().run_until_complete(
            self._run_async(filters=filters or {}, max_pages=max_pages)
        )
        self._metrics.finished_at = datetime.now(timezone.utc)
        log.info("pipeline.run.done", **self._metrics.to_dict())
        return self._metrics.to_dict()

    def run_incremental(
        self,
        filters: dict[str, Any] | None = None,
        **_: Any,
    ) -> dict[str, Any]:
        """
        Run an incremental ingestion pass (new/updated records only).

        Injects a ``minCreationDate`` filter based on the last successful
        run timestamp stored in the database.

        Parameters
        ----------
        filters:
            Additional source-specific filters.

        Returns
        -------
        Serialised :class:`PipelineMetrics` dict.
        """
        import asyncio

        repo = JobRepository()
        last_run = repo.get_last_run_timestamp(self.source_id)
        incremental_filters = dict(filters or {})
        if last_run:
            incremental_filters["minCreationDate"] = last_run.strftime("%Y-%m-%dT%H:%M:%SZ")

        log.info(
            "pipeline.incremental.start",
            source_id=self.source_id,
            since=incremental_filters.get("minCreationDate"),
        )
        asyncio.get_event_loop().run_until_complete(
            self._run_async(filters=incremental_filters, max_pages=20)
        )
        self._metrics.finished_at = datetime.now(timezone.utc)
        repo.record_run_timestamp(self.source_id, self._metrics.finished_at)
        log.info("pipeline.incremental.done", **self._metrics.to_dict())
        return self._metrics.to_dict()

    def run_batch(
        self,
        raw_job_ids: list[str],
    ) -> dict[str, Any]:
        """
        Re-process a list of raw job IDs through normalization and enrichment.

        Useful for reprocessing failed or stale records.

        Parameters
        ----------
        raw_job_ids:
            List of raw job UUIDs to reprocess.

        Returns
        -------
        Serialised :class:`PipelineMetrics` dict.
        """
        import asyncio

        log.info("pipeline.batch.start", count=len(raw_job_ids))
        asyncio.get_event_loop().run_until_complete(
            self._process_batch_async(raw_job_ids)
        )
        self._metrics.finished_at = datetime.now(timezone.utc)
        log.info("pipeline.batch.done", **self._metrics.to_dict())
        return self._metrics.to_dict()

    # ------------------------------------------------------------------
    # Async implementation
    # ------------------------------------------------------------------

    async def _run_async(
        self, filters: dict[str, Any], max_pages: int
    ) -> None:
        from packages.connectors.registry import ConnectorRegistry

        connector = ConnectorRegistry.get(self.source_id)

        for page in range(1, max_pages + 1):
            try:
                raw_jobs = await connector.fetch_job_list(page=page, filters=filters)
            except Exception as exc:
                log.error("pipeline.fetch_error", page=page, error=str(exc))
                self._metrics.errors += 1
                break

            if not raw_jobs:
                log.debug("pipeline.no_more_pages", page=page)
                break

            self._metrics.pages_fetched += 1
            self._metrics.raw_jobs_fetched += len(raw_jobs)

            for raw_job in raw_jobs:
                await self._process_one(connector, raw_job)

    async def _process_one(self, connector: Any, raw_job: Any) -> None:
        """Process a single raw job through the full pipeline stages."""
        try:
            # Stage 1: Normalize
            normalized = connector.normalize(raw_job)

            # Stage 2: Deduplicate
            if await connector.deduplicate(normalized):
                self._metrics.duplicates_skipped += 1
                return

            # Stage 3: Persist raw + normalized
            raw_id = await connector.store_raw(raw_job)
            normalized.raw_id = raw_id
            job_id = await connector.store_normalized(normalized)
            self._metrics.normalized += 1

            # Stage 4: Enrichment (skills, classification)
            try:
                from services.enrichment.enricher import JobEnricher

                enricher = JobEnricher()
                enricher.enrich(job_id)
                self._metrics.enriched += 1
            except Exception as exc:
                log.warning("pipeline.enrichment_error", job_id=job_id, error=str(exc))

        except Exception as exc:
            log.error("pipeline.process_error", error=str(exc))
            self._metrics.errors += 1
            self._metrics.dead_lettered += 1
            self._dead_letter(raw_job, str(exc))

    async def _process_batch_async(self, raw_job_ids: list[str]) -> None:
        repo = JobRepository()
        from packages.connectors.registry import ConnectorRegistry

        connector = ConnectorRegistry.get(self.source_id)

        for raw_id in raw_job_ids:
            try:
                raw_job = repo.get_raw_job(raw_id)
                if raw_job:
                    await self._process_one(connector, raw_job)
            except Exception as exc:
                log.error("pipeline.batch_item_error", raw_id=raw_id, error=str(exc))
                self._metrics.errors += 1

    def _dead_letter(self, raw_job: Any, reason: str) -> None:
        """Push a failed job to the Redis dead-letter queue."""
        try:
            import json
            import os
            import redis

            r = redis.from_url(os.environ.get("REDIS_URL", "redis://localhost:6379/0"))
            payload = json.dumps({
                "source_id": self.source_id,
                "pipeline_id": self.pipeline_id,
                "external_id": getattr(raw_job, "external_id", None),
                "reason": reason,
            })
            r.lpush("talentora:dlq:ingestion", payload)
        except Exception as exc:
            log.error("pipeline.dlq_push_failed", error=str(exc))


# ---------------------------------------------------------------------------
# JobRepository  (thin database abstraction)
# ---------------------------------------------------------------------------


class JobRepository:
    """
    Thin abstraction over the Talentora database for the pipeline and
    analytics layers.

    All query methods are synchronous; async wrappers are provided where
    the pipeline needs them.
    """

    # ------------------------------------------------------------------
    # Raw job CRUD
    # ------------------------------------------------------------------

    async def insert_raw(self, raw_job: Any) -> str:
        """Persist a raw job and return its assigned UUID."""
        raise NotImplementedError("Implement with your DB driver")

    def get_raw_job(self, raw_id: str) -> Any | None:
        """Retrieve a raw job by UUID."""
        raise NotImplementedError

    # ------------------------------------------------------------------
    # Normalized job CRUD
    # ------------------------------------------------------------------

    async def upsert_normalized(self, job: Any) -> str:
        """Insert or update a normalized job and return its UUID."""
        raise NotImplementedError

    async def exists_by_fingerprint(self, fingerprint: str) -> bool:
        """Check whether a job fingerprint already exists."""
        raise NotImplementedError

    # ------------------------------------------------------------------
    # Ingestion run tracking
    # ------------------------------------------------------------------

    def get_last_run_timestamp(self, source_id: str) -> datetime | None:
        """Return the datetime of the last successful run for a source."""
        raise NotImplementedError

    def record_run_timestamp(self, source_id: str, dt: datetime) -> None:
        """Persist the completion timestamp for a source run."""
        raise NotImplementedError

    # ------------------------------------------------------------------
    # Analytics query methods (used by TrendEngine / SalaryStats / MarketMetrics)
    # ------------------------------------------------------------------

    def count_skills_since(
        self, since: datetime, region: str | None = None
    ) -> dict[str, int]:
        raise NotImplementedError

    def count_skills_between(
        self, start: datetime, end: datetime, region: str | None = None
    ) -> dict[str, int]:
        raise NotImplementedError

    def avg_salary_by_skill(
        self, since: datetime, region: str | None = None
    ) -> dict[str, float]:
        raise NotImplementedError

    def salary_percentiles(
        self, role: str, region: str
    ) -> dict[str, Any] | None:
        raise NotImplementedError

    def count_skill_by_region(
        self, skill: str, since: datetime
    ) -> dict[str, int]:
        raise NotImplementedError

    def count_by_remote_type(
        self,
        since: datetime,
        region: str | None = None,
        role: str | None = None,
    ) -> dict[str, int]:
        raise NotImplementedError

    def get_salary_values(
        self,
        since: datetime,
        role: str | None,
        region: str | None,
        contract_type: str | None,
        currency: str,
        period: str,
    ) -> list[float]:
        raise NotImplementedError

    def list_active_regions(self) -> list[str]:
        raise NotImplementedError

    def count_jobs(
        self,
        since: datetime,
        region: str | None = None,
        role: str | None = None,
    ) -> int:
        raise NotImplementedError

    def count_new_jobs(
        self,
        since: datetime,
        region: str | None = None,
        role: str | None = None,
    ) -> int:
        raise NotImplementedError

    def avg_listing_age_days(
        self,
        since: datetime,
        region: str | None = None,
        role: str | None = None,
    ) -> float | None:
        raise NotImplementedError

    def count_by_contract_type(
        self,
        since: datetime,
        region: str | None = None,
        role: str | None = None,
    ) -> dict[str, int]:
        raise NotImplementedError

    def count_jobs_with_skill(
        self,
        skill: str,
        since: datetime,
        region: str | None = None,
    ) -> int:
        raise NotImplementedError

    def top_companies_by_listings(
        self,
        since: datetime,
        region: str | None = None,
        limit: int = 20,
    ) -> list[dict[str, Any]]:
        raise NotImplementedError
