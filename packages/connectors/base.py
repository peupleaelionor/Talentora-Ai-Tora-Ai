"""
Abstract base connector and shared data models for Talentora source connectors.

Every external data source (job board API, CSV import, RSS feed, …) must
implement ``BaseConnector`` so the ingestion pipeline can treat all sources
uniformly.
"""

from __future__ import annotations

import hashlib
import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------


@dataclass
class RawJob:
    """Unprocessed job record as received from a source."""

    source_id: str
    external_id: str
    raw_data: dict[str, Any]
    fetched_at: datetime = field(default_factory=datetime.utcnow)
    source_url: str | None = None
    raw_id: str | None = None  # populated after storage

    @property
    def fingerprint(self) -> str:
        """Stable SHA-256 fingerprint based on source + external id."""
        payload = f"{self.source_id}:{self.external_id}"
        return hashlib.sha256(payload.encode()).hexdigest()


@dataclass
class NormalizedJob:
    """Canonicalized job offer ready for persistence and analysis."""

    source_id: str
    external_id: str
    title: str
    company: str
    description: str
    location: str
    country: str  # ISO 3166-1 alpha-2
    language: str | None = None  # ISO 639-1
    url: str | None = None
    published_at: datetime | None = None
    contract_type: str | None = None  # CDI, CDD, freelance, …
    remote: str | None = None  # "full", "partial", "none"
    salary_min: float | None = None
    salary_max: float | None = None
    salary_currency: str | None = None
    salary_period: str | None = None  # "yearly", "monthly", "daily", "hourly"
    skills: list[str] = field(default_factory=list)
    raw_id: str | None = None
    job_id: str | None = None  # populated after storage
    extra: dict[str, Any] = field(default_factory=dict)

    @property
    def fingerprint(self) -> str:
        """SHA-256 fingerprint for deduplication."""
        payload = f"{self.source_id}:{self.external_id}"
        return hashlib.sha256(payload.encode()).hexdigest()


# ---------------------------------------------------------------------------
# Abstract base connector
# ---------------------------------------------------------------------------


class BaseConnector(ABC):
    """
    Contract that every Talentora source connector must fulfil.

    Subclasses implement ``fetch_job_list``, ``fetch_job_detail``, and
    ``normalize``.  Storage and de-duplication helpers are provided here
    and delegate to the shared database layer.
    """

    source_id: str
    source_name: str
    rate_limit: int = 60  # requests per minute

    # ------------------------------------------------------------------
    # Abstract interface
    # ------------------------------------------------------------------

    @abstractmethod
    async def fetch_job_list(self, page: int, filters: dict[str, Any]) -> list[RawJob]:
        """
        Retrieve a paginated list of raw jobs from the source.

        Parameters
        ----------
        page:
            1-indexed page number.
        filters:
            Source-specific query parameters (region, keyword, date, …).

        Returns
        -------
        List of :class:`RawJob` instances (may be empty on last page).
        """

    @abstractmethod
    async def fetch_job_detail(self, job_id: str) -> RawJob:
        """
        Retrieve full detail for a single job from the source.

        Parameters
        ----------
        job_id:
            Source-scoped identifier for the job.

        Returns
        -------
        :class:`RawJob` with ``raw_data`` populated with the full payload.
        """

    @abstractmethod
    def normalize(self, raw_job: RawJob) -> NormalizedJob:
        """
        Map a :class:`RawJob` to a :class:`NormalizedJob`.

        Parameters
        ----------
        raw_job:
            Raw job record as returned by fetch methods.

        Returns
        -------
        Canonicalized :class:`NormalizedJob`.
        """

    # ------------------------------------------------------------------
    # Shared helpers
    # ------------------------------------------------------------------

    async def deduplicate(self, job: NormalizedJob) -> bool:
        """
        Check whether a normalized job already exists in the database.

        Parameters
        ----------
        job:
            Normalized job to check.

        Returns
        -------
        ``True`` if the job is a duplicate (should be skipped).
        """
        try:
            from services.ingestion.pipeline import JobRepository

            repo = JobRepository()
            return await repo.exists_by_fingerprint(job.fingerprint)
        except Exception:
            return False

    async def store_raw(self, raw_job: RawJob) -> str:
        """
        Persist a raw job record and return its storage UUID.

        Parameters
        ----------
        raw_job:
            Raw job to persist.

        Returns
        -------
        UUID string assigned to the stored record.
        """
        try:
            from services.ingestion.pipeline import JobRepository

            repo = JobRepository()
            raw_id = await repo.insert_raw(raw_job)
            raw_job.raw_id = raw_id
            return raw_id
        except Exception as exc:
            raise RuntimeError(f"Failed to store raw job: {exc}") from exc

    async def store_normalized(self, job: NormalizedJob) -> str:
        """
        Persist a normalized job offer and return its storage UUID.

        Parameters
        ----------
        job:
            Normalized job to persist.

        Returns
        -------
        UUID string assigned to the stored record.
        """
        try:
            from services.ingestion.pipeline import JobRepository

            repo = JobRepository()
            job_id = await repo.upsert_normalized(job)
            job.job_id = job_id
            return job_id
        except Exception as exc:
            raise RuntimeError(f"Failed to store normalized job: {exc}") from exc

    # ------------------------------------------------------------------
    # Pagination helper
    # ------------------------------------------------------------------

    async def fetch_all_pages(
        self,
        filters: dict[str, Any] | None = None,
        max_pages: int = 100,
    ) -> list[RawJob]:
        """
        Convenience method: iterate pages until exhausted or ``max_pages``.

        Parameters
        ----------
        filters:
            Optional filters forwarded to ``fetch_job_list``.
        max_pages:
            Safety ceiling to prevent runaway pagination.

        Returns
        -------
        Aggregated list of :class:`RawJob` across all pages.
        """
        filters = filters or {}
        all_jobs: list[RawJob] = []

        for page in range(1, max_pages + 1):
            batch = await self.fetch_job_list(page=page, filters=filters)
            if not batch:
                break
            all_jobs.extend(batch)

        return all_jobs
