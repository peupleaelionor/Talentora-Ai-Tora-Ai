"""
Job enrichment service for Talentora.

``JobEnricher`` applies NLP-based enrichment (skill extraction,
role/seniority/industry classification) to a normalized job offer and
persists the results.  It also provides accessor helpers used by the
Celery analysis tasks.
"""

from __future__ import annotations

from typing import Any

import structlog

log = structlog.get_logger(__name__)


class JobEnricher:
    """
    Apply NLP enrichment to a normalized job offer.

    Methods are synchronous so they can be called from both sync
    (pipeline) and Celery (task) contexts.
    """

    def __init__(self) -> None:
        from packages.nlp.skill_extractor import SkillExtractor
        from packages.nlp.job_classifier import JobClassifier

        self._skill_extractor = SkillExtractor()
        self._classifier = JobClassifier()

    # ------------------------------------------------------------------
    # Enrichment entry point
    # ------------------------------------------------------------------

    def enrich(self, job_id: str) -> dict[str, Any]:
        """
        Run the full enrichment pipeline for a job offer.

        Extracts skills, classifies title/seniority/industry, and
        persists all results.

        Parameters
        ----------
        job_id:
            UUID of the normalized job offer.

        Returns
        -------
        dict summarising enrichment results.
        """
        logger = log.bind(job_id=job_id)
        logger.info("enricher.start")

        title = self.get_title(job_id)
        description = self.get_description(job_id)
        company = self.get_company(job_id)

        combined_text = f"{title}\n{description}"

        # Skill extraction
        skills = self._skill_extractor.extract(combined_text)
        self.save_skills(job_id, skills)

        # Classification
        canonical_role, role_conf = self._classifier.classify_title(title)
        seniority, sen_conf = self._classifier.classify_seniority(title, description)
        industry, ind_conf = self._classifier.classify_industry(description, company)

        classification = {
            "canonical_role": canonical_role,
            "role_confidence": role_conf,
            "seniority": seniority,
            "seniority_confidence": sen_conf,
            "industry": industry,
            "industry_confidence": ind_conf,
        }
        self.save_classification(job_id, classification)

        logger.info(
            "enricher.done",
            skills=len(skills),
            role=canonical_role,
            seniority=seniority,
        )
        return {"job_id": job_id, "skills_count": len(skills), **classification}

    # ------------------------------------------------------------------
    # Accessor helpers (used by Celery tasks)
    # ------------------------------------------------------------------

    def get_title(self, job_id: str) -> str:
        """Retrieve the job title for ``job_id``."""
        job = self._load_job(job_id)
        return job.get("title", "") if job else ""

    def get_description(self, job_id: str) -> str:
        """Retrieve the job description for ``job_id``."""
        job = self._load_job(job_id)
        return job.get("description", "") if job else ""

    def get_company(self, job_id: str) -> str:
        """Retrieve the company name for ``job_id``."""
        job = self._load_job(job_id)
        return job.get("company", "") if job else ""

    def get_skill_names(self, job_id: str) -> list[str]:
        """Return a list of normalised skill names for ``job_id``."""
        try:
            from services.ingestion.pipeline import JobRepository

            repo = JobRepository()
            return repo.get_skill_names(job_id)
        except Exception:
            return []

    # ------------------------------------------------------------------
    # Persistence helpers
    # ------------------------------------------------------------------

    def save_skills(self, job_id: str, skills: list[Any]) -> None:
        """
        Persist extracted skills against a job offer.

        Parameters
        ----------
        job_id:
            UUID of the normalized job.
        skills:
            List of :class:`~packages.nlp.skill_extractor.ExtractedSkill`.
        """
        try:
            from services.ingestion.pipeline import JobRepository

            repo = JobRepository()
            repo.upsert_skills(job_id, [s.to_dict() for s in skills])
        except Exception as exc:
            log.error("enricher.save_skills_failed", job_id=job_id, error=str(exc))

    def save_classification(self, job_id: str, classification: dict[str, Any]) -> None:
        """
        Persist role/seniority/industry classification for a job offer.

        Parameters
        ----------
        job_id:
            UUID of the normalized job.
        classification:
            Dict with classification fields.
        """
        try:
            from services.ingestion.pipeline import JobRepository

            repo = JobRepository()
            repo.upsert_classification(job_id, classification)
        except Exception as exc:
            log.error("enricher.save_classification_failed", job_id=job_id, error=str(exc))

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _load_job(job_id: str) -> dict[str, Any] | None:
        try:
            from services.ingestion.pipeline import JobRepository

            repo = JobRepository()
            return repo.get_normalized_job(job_id)
        except Exception as exc:
            log.error("enricher.load_job_failed", job_id=job_id, error=str(exc))
            return None
