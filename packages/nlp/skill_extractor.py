"""
Skill extraction module for Talentora NLP pipeline.

Combines rule-based pattern matching with spaCy NLP to identify and
normalise technical and soft skills in job descriptions.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum
from typing import Any

import structlog

log = structlog.get_logger(__name__)

# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------


class SourceType(str, Enum):
    PATTERN = "pattern"
    NLP = "nlp"
    COMBINED = "combined"


@dataclass
class ExtractedSkill:
    """A skill identified in a job description."""

    skill_name: str  # normalised lower-case name
    raw_text: str  # original text as found
    confidence: float  # 0.0 – 1.0
    source_type: SourceType

    def to_dict(self) -> dict[str, Any]:
        return {
            "skill_name": self.skill_name,
            "raw_text": self.raw_text,
            "confidence": self.confidence,
            "source_type": self.source_type.value,
        }


# ---------------------------------------------------------------------------
# Skill taxonomy / pattern dictionary
# ---------------------------------------------------------------------------

# Maps canonical normalised name -> list of surface forms (case-insensitive)
SKILL_PATTERNS: dict[str, list[str]] = {
    # Programming languages
    "python": ["Python", "python3", "Python 3"],
    "javascript": ["JavaScript", "JS", "javascript"],
    "typescript": ["TypeScript", "TS"],
    "java": ["Java", "Java SE", "Java EE"],
    "go": ["Go", "Golang"],
    "rust": ["Rust"],
    "c++": ["C\\+\\+", "C/C\\+\\+"],
    "c#": ["C#", "CSharp", "C Sharp"],
    "php": ["PHP"],
    "ruby": ["Ruby"],
    "scala": ["Scala"],
    "kotlin": ["Kotlin"],
    "swift": ["Swift"],
    "r": [r"\bR\b"],
    # Web frameworks
    "react": ["React", "ReactJS", "React.js"],
    "vue": ["Vue", "VueJS", "Vue.js"],
    "angular": ["Angular", "AngularJS"],
    "django": ["Django"],
    "fastapi": ["FastAPI"],
    "flask": ["Flask"],
    "spring": ["Spring", "Spring Boot", "Spring Framework"],
    "node.js": ["Node\\.js", "NodeJS", "Node JS"],
    "next.js": ["Next\\.js", "NextJS"],
    "nuxt": ["Nuxt\\.js", "NuxtJS"],
    # Data / ML
    "pytorch": ["PyTorch", "Pytorch"],
    "tensorflow": ["TensorFlow", "Tensorflow"],
    "scikit-learn": ["scikit-learn", "sklearn", "Scikit-Learn"],
    "pandas": ["pandas", "Pandas"],
    "numpy": ["NumPy", "numpy"],
    "spark": ["Apache Spark", "PySpark", "Spark"],
    "dbt": ["dbt", "DBT"],
    "airflow": ["Apache Airflow", "Airflow"],
    "mlflow": ["MLflow", "MLFlow"],
    # Databases
    "postgresql": ["PostgreSQL", "Postgres", "pg"],
    "mysql": ["MySQL"],
    "mongodb": ["MongoDB", "Mongo"],
    "redis": ["Redis"],
    "elasticsearch": ["Elasticsearch", "ElasticSearch", "OpenSearch"],
    "cassandra": ["Cassandra", "Apache Cassandra"],
    "bigquery": ["BigQuery", "Google BigQuery"],
    "snowflake": ["Snowflake"],
    # Cloud
    "aws": ["AWS", "Amazon Web Services"],
    "gcp": ["GCP", "Google Cloud", "Google Cloud Platform"],
    "azure": ["Azure", "Microsoft Azure"],
    # DevOps / infra
    "docker": ["Docker"],
    "kubernetes": ["Kubernetes", "K8s"],
    "terraform": ["Terraform"],
    "github_actions": ["GitHub Actions", "GH Actions"],
    "gitlab_ci": ["GitLab CI", "GitLab CI/CD"],
    "ansible": ["Ansible"],
    "jenkins": ["Jenkins"],
    "linux": ["Linux", "Unix"],
    "git": ["Git", "GitHub", "GitLab"],
    # Architecture
    "rest_api": ["REST API", "RESTful", "REST"],
    "graphql": ["GraphQL"],
    "grpc": ["gRPC"],
    "microservices": ["microservices", "micro-services"],
    "event_driven": ["event-driven", "event driven", "Kafka", "Apache Kafka", "RabbitMQ"],
    # Soft skills
    "agile": ["Agile", "Scrum", "Kanban", "SAFe"],
    "communication": ["communication", "communicating"],
    "teamwork": ["teamwork", "team player", "travail en équipe"],
    "leadership": ["leadership", "lead", "manager"],
}


def _build_compiled_patterns() -> dict[str, re.Pattern[str]]:
    compiled: dict[str, re.Pattern[str]] = {}
    for canonical, surfaces in SKILL_PATTERNS.items():
        alternatives = "|".join(
            rf"(?<!\w){re.escape(s) if not s.startswith('\\') else s}(?!\w)"
            if not s.startswith(r"\b")
            else s
            for s in surfaces
        )
        compiled[canonical] = re.compile(f"({alternatives})", re.IGNORECASE)
    return compiled


_COMPILED_PATTERNS: dict[str, re.Pattern[str]] = _build_compiled_patterns()


# ---------------------------------------------------------------------------
# Extractor
# ---------------------------------------------------------------------------


class SkillExtractor:
    """
    Two-stage skill extractor combining rule-based patterns with spaCy NLP.

    Parameters
    ----------
    use_nlp:
        When ``True``, also run spaCy NER to catch skills not in the
        pattern dictionary.  Requires ``fr_core_news_md`` or
        ``en_core_web_md`` to be installed.
    nlp_model:
        spaCy model name to load.
    """

    def __init__(
        self,
        use_nlp: bool = True,
        nlp_model: str = "fr_core_news_md",
    ) -> None:
        self._use_nlp = use_nlp
        self._nlp_model = nlp_model
        self._nlp: Any = None  # lazy-loaded

    def _load_nlp(self) -> Any:
        if self._nlp is None:
            try:
                import spacy

                self._nlp = spacy.load(self._nlp_model)
            except OSError:
                try:
                    import spacy

                    self._nlp = spacy.load("en_core_web_md")
                except OSError:
                    log.warning("skill_extractor.no_spacy_model", model=self._nlp_model)
                    self._nlp = None
        return self._nlp

    # ------------------------------------------------------------------
    # Pattern-based extraction
    # ------------------------------------------------------------------

    def _extract_by_patterns(self, text: str) -> list[ExtractedSkill]:
        found: list[ExtractedSkill] = []
        seen_canonical: set[str] = set()

        for canonical, pattern in _COMPILED_PATTERNS.items():
            if canonical in seen_canonical:
                continue
            matches = pattern.findall(text)
            if matches:
                raw = matches[0] if isinstance(matches[0], str) else matches[0][0]
                found.append(
                    ExtractedSkill(
                        skill_name=canonical,
                        raw_text=raw,
                        confidence=0.95,
                        source_type=SourceType.PATTERN,
                    )
                )
                seen_canonical.add(canonical)

        return found

    # ------------------------------------------------------------------
    # NLP-based extraction
    # ------------------------------------------------------------------

    def _extract_by_nlp(self, text: str, already_found: set[str]) -> list[ExtractedSkill]:
        nlp = self._load_nlp()
        if nlp is None:
            return []

        doc = nlp(text[:100_000])  # spaCy has a default limit
        skills: list[ExtractedSkill] = []

        for ent in doc.ents:
            if ent.label_ not in {"MISC", "ORG", "PRODUCT"}:
                continue
            normalised = self._normalise_name(ent.text)
            if not normalised or normalised in already_found or len(normalised) < 2:
                continue
            skills.append(
                ExtractedSkill(
                    skill_name=normalised,
                    raw_text=ent.text,
                    confidence=0.60,
                    source_type=SourceType.NLP,
                )
            )
            already_found.add(normalised)

        return skills

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    @staticmethod
    def _normalise_name(name: str) -> str:
        """Lowercase and strip punctuation for canonical skill names."""
        return re.sub(r"[^\w+#.]", "_", name.strip().lower()).strip("_")

    def extract(self, text: str) -> list[ExtractedSkill]:
        """
        Extract skills from free-form job text.

        Parameters
        ----------
        text:
            Combined job title + description (plain text, HTML stripped).

        Returns
        -------
        Deduplicated list of :class:`ExtractedSkill`, ordered by
        confidence descending.
        """
        if not text:
            return []

        pattern_skills = self._extract_by_patterns(text)
        found_names = {s.skill_name for s in pattern_skills}

        nlp_skills: list[ExtractedSkill] = []
        if self._use_nlp:
            nlp_skills = self._extract_by_nlp(text, found_names)

        all_skills = pattern_skills + nlp_skills
        all_skills.sort(key=lambda s: s.confidence, reverse=True)

        log.debug(
            "skill_extractor.extracted",
            pattern_count=len(pattern_skills),
            nlp_count=len(nlp_skills),
        )
        return all_skills
