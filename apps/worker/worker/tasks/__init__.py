"""Celery task modules for the Talentora worker."""

from worker.tasks.ingestion import (
    run_ingestion_pipeline,
    fetch_jobs_from_source,
    process_raw_job,
    run_all_sources,
)
from worker.tasks.normalization import (
    normalize_job_offer,
    clean_html_description,
    detect_language,
    extract_salary,
)
from worker.tasks.analysis import (
    extract_skills_from_job,
    classify_job_title,
    compute_trends,
    generate_embeddings,
)

__all__ = [
    "run_ingestion_pipeline",
    "fetch_jobs_from_source",
    "process_raw_job",
    "run_all_sources",
    "normalize_job_offer",
    "clean_html_description",
    "detect_language",
    "extract_salary",
    "extract_skills_from_job",
    "classify_job_title",
    "compute_trends",
    "generate_embeddings",
]
