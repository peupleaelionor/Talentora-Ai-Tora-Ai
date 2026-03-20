"""
Job offer normalization service for Talentora.

``JobNormalizer`` loads a raw job record from the database, applies
HTML cleaning, language detection, salary extraction, and field
normalization, then persists the result via the connector interface.
"""

from __future__ import annotations

from typing import Any

import structlog

log = structlog.get_logger(__name__)


class JobNormalizer:
    """
    Normalize a persisted raw job record into a ``NormalizedJob``.

    The normalizer is connector-agnostic: it retrieves the source_id from
    the raw record and delegates field mapping to the appropriate
    connector's ``normalize()`` method, then applies cross-source NLP
    enrichment (HTML cleaning, language detection, salary extraction).
    """

    def __init__(self) -> None:
        from packages.nlp.text_cleaner import TextCleaner
        from packages.nlp.salary_parser import SalaryParser

        self._cleaner = TextCleaner()
        self._salary_parser = SalaryParser()

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def normalize(self, raw_job_id: str) -> str | None:
        """
        Normalize a raw job and persist the result.

        Parameters
        ----------
        raw_job_id:
            UUID of the raw job record.

        Returns
        -------
        UUID of the persisted normalized job, or ``None`` if the record
        was detected as a duplicate.
        """
        logger = log.bind(raw_job_id=raw_job_id)
        logger.info("normalizer.start")

        raw_job = self._load_raw(raw_job_id)
        if raw_job is None:
            logger.warning("normalizer.raw_not_found")
            return None

        # Delegate structural field mapping to the connector
        from packages.connectors.registry import ConnectorRegistry

        connector = ConnectorRegistry.get(raw_job.source_id)
        normalized = connector.normalize(raw_job)

        # NLP post-processing
        normalized.description = self._clean_description(normalized.description)
        normalized.language = self._detect_language(normalized.description)
        self._enrich_salary(normalized)

        # Deduplication
        import asyncio

        is_dup = asyncio.get_event_loop().run_until_complete(
            connector.deduplicate(normalized)
        )
        if is_dup:
            logger.info("normalizer.duplicate_skipped")
            return None

        # Persist
        job_id = asyncio.get_event_loop().run_until_complete(
            connector.store_normalized(normalized)
        )
        logger.info("normalizer.done", job_id=job_id)
        return job_id

    # ------------------------------------------------------------------
    # NLP helpers
    # ------------------------------------------------------------------

    def _clean_description(self, description: str) -> str:
        """Strip HTML and normalize whitespace in the job description."""
        cleaned = self._cleaner.clean_html(description)
        cleaned = self._cleaner.remove_pii(cleaned)
        return self._cleaner.normalize_whitespace(cleaned)

    def _detect_language(self, text: str) -> str | None:
        """Return ISO 639-1 language code or None."""
        lang, confidence = self._cleaner.detect_language(text)
        if confidence >= 0.80 and lang != "unknown":
            return lang
        return None

    def _enrich_salary(self, normalized: Any) -> None:
        """
        Attempt to extract salary from description when not already set.

        Populates ``salary_min``, ``salary_max``, ``salary_currency``, and
        ``salary_period`` on ``normalized`` if they are missing.
        """
        if normalized.salary_min is not None:
            return  # already populated by the connector

        salary = self._salary_parser.extract_salary(normalized.description)
        if salary is None:
            return

        if salary.confidence >= 0.70:
            normalized.salary_min = salary.min_value
            normalized.salary_max = salary.max_value
            normalized.salary_currency = salary.currency
            normalized.salary_period = salary.period

    # ------------------------------------------------------------------
    # Database helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _load_raw(raw_job_id: str) -> Any | None:
        """Load a raw job record from the database."""
        try:
            from services.ingestion.pipeline import JobRepository

            repo = JobRepository()
            return repo.get_raw_job(raw_job_id)
        except Exception as exc:
            log.error("normalizer.load_raw_failed", raw_job_id=raw_job_id, error=str(exc))
            return None
