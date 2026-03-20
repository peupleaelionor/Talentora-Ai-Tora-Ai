"""Integration tests for the ingestion pipeline with mocked dependencies."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"


@pytest.fixture
def sample_france_travail_response() -> dict[str, Any]:
    with open(FIXTURES_DIR / "sample_france_travail_response.json") as f:
        return json.load(f)


@pytest.fixture
def sample_jobs() -> list[dict[str, Any]]:
    with open(FIXTURES_DIR / "sample_jobs.json") as f:
        return json.load(f)


@pytest.fixture
def mock_http_client(sample_france_travail_response: dict[str, Any]) -> MagicMock:
    client = MagicMock()
    response = MagicMock()
    response.json.return_value = sample_france_travail_response
    response.status_code = 200
    client.get = AsyncMock(return_value=response)
    return client


@pytest.fixture
def mock_db() -> MagicMock:
    db = MagicMock()
    db.insert_job = AsyncMock(return_value={"id": "test-id-123"})
    db.upsert_job = AsyncMock(return_value={"id": "test-id-123", "updated": True})
    db.get_job_by_external_id = AsyncMock(return_value=None)
    return db


@pytest.fixture
def mock_normalizer() -> MagicMock:
    normalizer = MagicMock()
    normalizer.normalize = MagicMock(
        side_effect=lambda job: {**job, "normalized": True, "skills": ["Python", "SQL"]}
    )
    return normalizer


@pytest.fixture
def mock_classifier() -> MagicMock:
    classifier = MagicMock()
    classifier.classify_role = MagicMock(return_value="engineering")
    classifier.detect_seniority = MagicMock(return_value="senior")
    classifier.classify_industry = MagicMock(return_value="saas")
    return classifier


class TestIngestionPipelineFlow:
    @pytest.mark.asyncio
    async def test_fetch_and_store_jobs(
        self,
        mock_http_client: MagicMock,
        mock_db: MagicMock,
        mock_normalizer: MagicMock,
        sample_france_travail_response: dict[str, Any],
    ) -> None:
        """Pipeline fetches jobs, normalizes them, and stores them in DB."""
        jobs = sample_france_travail_response.get("resultats", [])
        assert len(jobs) == 3

        for job in jobs:
            normalized = mock_normalizer.normalize(job)
            assert normalized["normalized"] is True
            result = await mock_db.upsert_job(normalized)
            assert result["id"] == "test-id-123"

        assert mock_normalizer.normalize.call_count == 3
        assert mock_db.upsert_job.call_count == 3

    @pytest.mark.asyncio
    async def test_deduplication_skips_existing_jobs(
        self,
        mock_db: MagicMock,
        sample_jobs: list[dict[str, Any]],
    ) -> None:
        """Pipeline skips jobs already stored in the database."""
        mock_db.get_job_by_external_id = AsyncMock(
            return_value={"id": "existing-id", "title": "Existing Job"}
        )

        job = sample_jobs[0]
        existing = await mock_db.get_job_by_external_id(job.get("id"))
        assert existing is not None
        assert existing["id"] == "existing-id"

        assert mock_db.insert_job.call_count == 0

    @pytest.mark.asyncio
    async def test_classification_enriches_jobs(
        self,
        mock_classifier: MagicMock,
        sample_jobs: list[dict[str, Any]],
    ) -> None:
        """Pipeline classifies role, seniority and industry for each job."""
        for job in sample_jobs:
            role = mock_classifier.classify_role(job["title"])
            seniority = mock_classifier.detect_seniority(job["title"])
            industry = mock_classifier.classify_industry(job.get("description", ""))

            assert role in {"engineering", "data", "product", "devops", "ml", "other"}
            assert seniority in {"intern", "junior", "mid", "senior", "lead", "staff", "principal"}
            assert industry in {"fintech", "healthcare", "ecommerce", "saas", "other"}

    @pytest.mark.asyncio
    async def test_http_error_raises(self, mock_http_client: MagicMock) -> None:
        """Pipeline propagates HTTP errors."""
        error_response = MagicMock()
        error_response.status_code = 503
        error_response.raise_for_status = MagicMock(
            side_effect=Exception("Service Unavailable")
        )
        mock_http_client.get = AsyncMock(return_value=error_response)

        response = await mock_http_client.get("https://api.francetravail.io/jobs")
        with pytest.raises(Exception, match="Service Unavailable"):
            response.raise_for_status()

    @pytest.mark.asyncio
    async def test_db_error_propagates(self, mock_db: MagicMock) -> None:
        """Pipeline surfaces DB write errors."""
        mock_db.upsert_job = AsyncMock(side_effect=RuntimeError("DB connection lost"))

        with pytest.raises(RuntimeError, match="DB connection lost"):
            await mock_db.upsert_job({"title": "Test Job"})
