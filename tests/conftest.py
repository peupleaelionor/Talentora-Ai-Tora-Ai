"""
Pytest configuration and shared fixtures for Talentora AI tests.
"""

import json
import pytest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def sample_job_text() -> str:
    """Plain text job description for NLP tests."""
    return """
    We are looking for a Senior Software Engineer to join our growing team in Paris.

    Requirements:
    - 5+ years of experience with Python and TypeScript
    - Strong knowledge of React, Next.js, and Node.js
    - Experience with PostgreSQL, Redis, and Docker
    - Familiarity with AWS services (S3, Lambda, RDS)
    - Knowledge of REST APIs and GraphQL
    - Experience with CI/CD pipelines (GitHub Actions, Jenkins)

    Nice to have:
    - Experience with Kubernetes and Terraform
    - Knowledge of machine learning frameworks (PyTorch, TensorFlow)

    Salary: 70,000€ - 90,000€ per year
    Contract: CDI (permanent)
    Remote: Hybrid (3 days remote)
    """


@pytest.fixture
def sample_html_job() -> str:
    """HTML job description for parsing tests."""
    return """
    <html>
    <body>
    <h1>Data Engineer - Paris</h1>
    <div class="description">
        <p>We are hiring a <strong>Data Engineer</strong> to build our data platform.</p>
        <ul>
            <li>Experience with Apache Spark and Kafka</li>
            <li>Python and SQL expertise</li>
            <li>Knowledge of dbt and Airflow</li>
        </ul>
        <p>Salary range: <strong>55k€ - 75k€</strong></p>
        <p>Contact: jobs@example.com</p>
    </div>
    </body>
    </html>
    """


@pytest.fixture
def sample_jobs_fixture() -> list:
    """Load sample jobs from fixtures file."""
    with open(FIXTURES_DIR / "sample_jobs.json") as f:
        return json.load(f)


@pytest.fixture
def sample_france_travail_response() -> dict:
    """Load sample France Travail API response from fixtures."""
    with open(FIXTURES_DIR / "sample_france_travail_response.json") as f:
        return json.load(f)


@pytest.fixture
def mock_db_session():
    """Mock database session for service tests."""
    session = AsyncMock()
    session.execute = AsyncMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.close = AsyncMock()
    return session


@pytest.fixture
def mock_redis_client():
    """Mock Redis client for caching tests."""
    client = MagicMock()
    client.get = MagicMock(return_value=None)
    client.set = MagicMock(return_value=True)
    client.delete = MagicMock(return_value=1)
    return client
