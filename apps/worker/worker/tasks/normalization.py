"""
Normalization Celery tasks for the Talentora worker.

Cleans raw job data, detects language, extracts salary information,
and persists normalized job offers.
"""

from __future__ import annotations

from typing import Any

import structlog

from worker.celery_app import app

log = structlog.get_logger(__name__)


# ---------------------------------------------------------------------------
# Task: normalize_job_offer
# ---------------------------------------------------------------------------


@app.task(
    bind=True,
    name="worker.tasks.normalization.normalize_job_offer",
    max_retries=3,
    default_retry_delay=15,
    acks_late=True,
)
def normalize_job_offer(self, raw_job_id: str) -> str | None:
    """
    Normalize a raw job record and persist the result.

    Applies HTML cleaning, language detection, salary extraction, and
    field normalization before writing the normalized job offer.

    Parameters
    ----------
    raw_job_id:
        UUID of the raw job record to normalize.

    Returns
    -------
    UUID of the persisted normalized job, or ``None`` on de-duplication.
    """
    logger = log.bind(raw_job_id=raw_job_id)
    logger.info("normalize_job_offer.start")

    try:
        from services.normalization.normalizer import JobNormalizer

        normalizer = JobNormalizer()
        job_id = normalizer.normalize(raw_job_id)

        logger.info("normalize_job_offer.complete", job_id=job_id)
        return job_id

    except Exception as exc:
        logger.warning("normalize_job_offer.retry", error=str(exc))
        try:
            raise self.retry(exc=exc, countdown=15 * (self.request.retries + 1))
        except Exception:
            logger.error("normalize_job_offer.failed", raw_job_id=raw_job_id, error=str(exc))
            raise


# ---------------------------------------------------------------------------
# Task: clean_html_description
# ---------------------------------------------------------------------------


@app.task(
    name="worker.tasks.normalization.clean_html_description",
    acks_late=True,
)
def clean_html_description(description: str) -> str:
    """
    Strip HTML markup and normalize whitespace in a job description.

    Parameters
    ----------
    description:
        Raw HTML or plain-text job description.

    Returns
    -------
    Cleaned plain-text string.
    """
    from packages.nlp.text_cleaner import TextCleaner

    cleaner = TextCleaner()
    cleaned = cleaner.clean_html(description)
    cleaned = cleaner.normalize_whitespace(cleaned)
    log.debug("clean_html_description.done", original_len=len(description), cleaned_len=len(cleaned))
    return cleaned


# ---------------------------------------------------------------------------
# Task: detect_language
# ---------------------------------------------------------------------------


@app.task(
    name="worker.tasks.normalization.detect_language",
    acks_late=True,
)
def detect_language(text: str) -> dict[str, Any]:
    """
    Detect the language of the provided text.

    Parameters
    ----------
    text:
        Plain-text content to analyse.

    Returns
    -------
    dict with ``language`` (ISO 639-1 code) and ``confidence`` (0–1 float).
    """
    from packages.nlp.text_cleaner import TextCleaner

    cleaner = TextCleaner()
    lang, confidence = cleaner.detect_language(text)
    log.debug("detect_language.done", language=lang, confidence=confidence)
    return {"language": lang, "confidence": confidence}


# ---------------------------------------------------------------------------
# Task: extract_salary
# ---------------------------------------------------------------------------


@app.task(
    name="worker.tasks.normalization.extract_salary",
    acks_late=True,
)
def extract_salary(text: str) -> dict[str, Any] | None:
    """
    Extract structured salary information from free-form text.

    Parameters
    ----------
    text:
        Job description or salary field text.

    Returns
    -------
    dict with ``min``, ``max``, ``currency``, ``period``, ``confidence``,
    or ``None`` when no salary information is found.
    """
    from packages.nlp.salary_parser import SalaryParser

    parser = SalaryParser()
    salary_info = parser.extract_salary(text)

    if salary_info is None:
        log.debug("extract_salary.not_found")
        return None

    result = {
        "min": salary_info.min_value,
        "max": salary_info.max_value,
        "currency": salary_info.currency,
        "period": salary_info.period,
        "confidence": salary_info.confidence,
    }
    log.debug("extract_salary.found", result=result)
    return result
