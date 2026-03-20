"""Unit tests for job classifier."""
import pytest
from packages.nlp.job_classifier import JobClassifier


@pytest.fixture
def classifier() -> JobClassifier:
    return JobClassifier()


class TestRoleClassification:
    def test_software_engineer(self, classifier: JobClassifier) -> None:
        assert classifier.classify_role("Software Engineer") == "engineering"

    def test_backend_developer(self, classifier: JobClassifier) -> None:
        assert classifier.classify_role("Backend Developer Python") == "engineering"

    def test_data_engineer(self, classifier: JobClassifier) -> None:
        assert classifier.classify_role("Data Engineer") == "data"

    def test_product_manager(self, classifier: JobClassifier) -> None:
        assert classifier.classify_role("Product Manager") == "product"

    def test_devops_engineer(self, classifier: JobClassifier) -> None:
        assert classifier.classify_role("DevOps Engineer") == "devops"

    def test_ml_engineer(self, classifier: JobClassifier) -> None:
        assert classifier.classify_role("Machine Learning Engineer") == "ml"

    def test_unknown_role_returns_other(self, classifier: JobClassifier) -> None:
        assert classifier.classify_role("Astronaut") == "other"


class TestSeniorityDetection:
    def test_junior(self, classifier: JobClassifier) -> None:
        assert classifier.detect_seniority("Junior Software Engineer") == "junior"

    def test_senior(self, classifier: JobClassifier) -> None:
        assert classifier.detect_seniority("Senior Backend Developer") == "senior"

    def test_lead(self, classifier: JobClassifier) -> None:
        assert classifier.detect_seniority("Lead Data Engineer") == "lead"

    def test_staff(self, classifier: JobClassifier) -> None:
        assert classifier.detect_seniority("Staff Engineer") == "staff"

    def test_principal(self, classifier: JobClassifier) -> None:
        assert classifier.detect_seniority("Principal Software Engineer") == "principal"

    def test_mid_level_default(self, classifier: JobClassifier) -> None:
        assert classifier.detect_seniority("Software Engineer") == "mid"

    def test_intern(self, classifier: JobClassifier) -> None:
        assert classifier.detect_seniority("Intern Software Engineer") == "intern"

    def test_case_insensitive(self, classifier: JobClassifier) -> None:
        assert classifier.detect_seniority("SENIOR developer") == "senior"


class TestIndustryClassification:
    def test_fintech(self, classifier: JobClassifier) -> None:
        description = "Join our fintech startup disrupting banking and payments."
        assert classifier.classify_industry(description) == "fintech"

    def test_healthcare(self, classifier: JobClassifier) -> None:
        description = "Build health data platforms for hospitals and clinics."
        assert classifier.classify_industry(description) == "healthcare"

    def test_ecommerce(self, classifier: JobClassifier) -> None:
        description = "Scale our e-commerce marketplace serving millions of buyers."
        assert classifier.classify_industry(description) == "ecommerce"

    def test_saas(self, classifier: JobClassifier) -> None:
        description = "Grow our B2B SaaS platform used by enterprise customers."
        assert classifier.classify_industry(description) == "saas"

    def test_unknown_industry(self, classifier: JobClassifier) -> None:
        description = "A company doing various things."
        assert classifier.classify_industry(description) == "other"
