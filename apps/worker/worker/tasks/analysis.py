"""
AI analysis Celery tasks for the Talentora worker.

Handles skill extraction, job title classification, market trend
computation, and vector embedding generation.
"""

from __future__ import annotations

from typing import Any

import structlog

from worker.celery_app import app

log = structlog.get_logger(__name__)


# ---------------------------------------------------------------------------
# Task: extract_skills_from_job
# ---------------------------------------------------------------------------


@app.task(
    bind=True,
    name="worker.tasks.analysis.extract_skills_from_job",
    max_retries=3,
    default_retry_delay=20,
    rate_limit="60/m",
    acks_late=True,
)
def extract_skills_from_job(self, job_id: str) -> dict[str, Any]:
    """
    Extract and persist skills from a normalized job offer.

    Combines rule-based pattern matching with spaCy NLP extraction and
    stores confidence-scored results against the job record.

    Parameters
    ----------
    job_id:
        UUID of the normalized job offer.

    Returns
    -------
    dict with ``job_id`` and ``skills`` list of ``{name, confidence, source}``.
    """
    logger = log.bind(job_id=job_id)
    logger.info("extract_skills.start")

    try:
        from packages.nlp.skill_extractor import SkillExtractor
        from services.enrichment.enricher import JobEnricher

        extractor = SkillExtractor()
        enricher = JobEnricher()

        description = enricher.get_description(job_id)
        title = enricher.get_title(job_id)

        skills = extractor.extract(f"{title}\n{description}")

        enricher.save_skills(job_id, skills)

        result = [
            {"name": s.skill_name, "confidence": s.confidence, "source": s.source_type}
            for s in skills
        ]
        logger.info("extract_skills.complete", count=len(result))
        return {"job_id": job_id, "skills": result}

    except Exception as exc:
        logger.warning("extract_skills.retry", error=str(exc))
        try:
            raise self.retry(exc=exc, countdown=20 * (self.request.retries + 1))
        except Exception:
            logger.error("extract_skills.failed", job_id=job_id, error=str(exc))
            raise


# ---------------------------------------------------------------------------
# Task: classify_job_title
# ---------------------------------------------------------------------------


@app.task(
    bind=True,
    name="worker.tasks.analysis.classify_job_title",
    max_retries=3,
    default_retry_delay=10,
    acks_late=True,
)
def classify_job_title(self, job_id: str) -> dict[str, Any]:
    """
    Classify a job title into a canonical role, seniority, and industry.

    Parameters
    ----------
    job_id:
        UUID of the normalized job offer.

    Returns
    -------
    dict with ``job_id``, ``canonical_role``, ``seniority``, ``industry``,
    and respective ``confidence`` scores.
    """
    logger = log.bind(job_id=job_id)
    logger.info("classify_job_title.start")

    try:
        from packages.nlp.job_classifier import JobClassifier
        from services.enrichment.enricher import JobEnricher

        classifier = JobClassifier()
        enricher = JobEnricher()

        title = enricher.get_title(job_id)
        description = enricher.get_description(job_id)
        company = enricher.get_company(job_id)

        canonical_role, role_confidence = classifier.classify_title(title)
        seniority, seniority_confidence = classifier.classify_seniority(title, description)
        industry, industry_confidence = classifier.classify_industry(description, company)

        classification = {
            "canonical_role": canonical_role,
            "role_confidence": role_confidence,
            "seniority": seniority,
            "seniority_confidence": seniority_confidence,
            "industry": industry,
            "industry_confidence": industry_confidence,
        }
        enricher.save_classification(job_id, classification)

        logger.info("classify_job_title.complete", canonical_role=canonical_role)
        return {"job_id": job_id, **classification}

    except Exception as exc:
        logger.warning("classify_job_title.retry", error=str(exc))
        try:
            raise self.retry(exc=exc, countdown=10 * (self.request.retries + 1))
        except Exception:
            logger.error("classify_job_title.failed", job_id=job_id, error=str(exc))
            raise


# ---------------------------------------------------------------------------
# Task: compute_trends
# ---------------------------------------------------------------------------


@app.task(
    bind=True,
    name="worker.tasks.analysis.compute_trends",
    max_retries=2,
    default_retry_delay=120,
    acks_late=True,
    track_started=True,
    time_limit=3600,
    soft_time_limit=3000,
)
def compute_trends(
    self,
    timeframe: str = "7d",
    region: str | None = None,
) -> dict[str, Any]:
    """
    Compute market trend snapshots and persist them.

    Covers skill demand, salary trends, regional demand, emerging skills,
    and remote work patterns.

    Parameters
    ----------
    timeframe:
        Rolling window string: ``"7d"``, ``"30d"``, ``"90d"``, ``"1y"``.
    region:
        Optional ISO 3166-1 alpha-2 country code or NUTS region code.

    Returns
    -------
    dict summarising computed trend categories and record counts.
    """
    logger = log.bind(timeframe=timeframe, region=region)
    logger.info("compute_trends.start")

    try:
        from packages.analytics.trend_engine import TrendEngine

        engine = TrendEngine()
        summary: dict[str, Any] = {}

        skill_trends = engine.compute_skill_trends(timeframe=timeframe, region=region)
        summary["skill_trends"] = len(skill_trends)

        emerging = engine.detect_emerging_skills(timeframe=timeframe, threshold=0.2)
        summary["emerging_skills"] = len(emerging)

        remote = engine.compute_remote_trends(timeframe=timeframe)
        summary["remote_trend"] = remote.remote_percentage if remote else None

        logger.info("compute_trends.complete", summary=summary)
        return {"timeframe": timeframe, "region": region, **summary}

    except Exception as exc:
        logger.warning("compute_trends.retry", error=str(exc))
        try:
            raise self.retry(exc=exc, countdown=120)
        except Exception:
            logger.error("compute_trends.failed", error=str(exc))
            raise


# ---------------------------------------------------------------------------
# Task: generate_embeddings
# ---------------------------------------------------------------------------


@app.task(
    bind=True,
    name="worker.tasks.analysis.generate_embeddings",
    max_retries=3,
    default_retry_delay=30,
    rate_limit="30/m",
    acks_late=True,
)
def generate_embeddings(self, job_id: str) -> dict[str, Any]:
    """
    Generate and store a vector embedding for a job offer.

    The embedding combines title, description, and extracted skills into
    a single dense vector for similarity search.

    Parameters
    ----------
    job_id:
        UUID of the normalized job offer.

    Returns
    -------
    dict with ``job_id`` and ``embedding_dim``.
    """
    logger = log.bind(job_id=job_id)
    logger.info("generate_embeddings.start")

    try:
        from services.enrichment.enricher import JobEnricher
        from services.search_engine.indexer import SearchIndexer

        enricher = JobEnricher()
        indexer = SearchIndexer()

        title = enricher.get_title(job_id)
        description = enricher.get_description(job_id)
        skills_text = " ".join(enricher.get_skill_names(job_id))

        text = f"{title} {skills_text} {description}"
        embedding = indexer.embed(text)
        indexer.upsert(job_id, embedding)

        logger.info("generate_embeddings.complete", dim=len(embedding))
        return {"job_id": job_id, "embedding_dim": len(embedding)}

    except Exception as exc:
        logger.warning("generate_embeddings.retry", error=str(exc))
        try:
            raise self.retry(exc=exc, countdown=30 * (self.request.retries + 1))
        except Exception:
            logger.error("generate_embeddings.failed", job_id=job_id, error=str(exc))
            raise
