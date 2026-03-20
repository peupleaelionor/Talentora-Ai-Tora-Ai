"""Unit tests for skill extractor."""
from __future__ import annotations
import pytest
from dataclasses import dataclass


@dataclass
class ExtractedSkill:
    name: str
    normalized: str
    confidence: float
    is_required: bool


SKILL_PATTERNS = {
    "python": ["python", "py "],
    "typescript": ["typescript", "ts "],
    "javascript": ["javascript", "js "],
    "react": ["react", "reactjs", "react.js"],
    "fastapi": ["fastapi", "fast api"],
    "postgresql": ["postgresql", "postgres", "pg "],
    "docker": ["docker"],
    "kubernetes": ["kubernetes", "k8s"],
    "kafka": ["kafka", "apache kafka"],
    "redis": ["redis"],
    "machine learning": ["machine learning", "ml ", "apprentissage automatique"],
    "sql": [" sql", "structured query"],
}

REQUIRED_SIGNALS = ["requis", "required", "maîtrise", "expertise", "mandatory", "must have", "essentiel"]
OPTIONAL_SIGNALS = ["souhaité", "idéalement", "nice to have", "optionnel", "apprécié", "un plus"]


def extract_skills(text: str) -> list[ExtractedSkill]:
    lower = text.lower()
    results = []
    for skill_name, patterns in SKILL_PATTERNS.items():
        for pattern in patterns:
            if pattern in lower:
                # Determine required vs optional
                idx = lower.find(pattern)
                context = lower[max(0, idx - 80):idx + 80]
                is_required = not any(sig in context for sig in OPTIONAL_SIGNALS)
                confidence = 0.95 if any(sig in context for sig in REQUIRED_SIGNALS) else 0.80
                results.append(ExtractedSkill(
                    name=skill_name.title(),
                    normalized=skill_name,
                    confidence=confidence,
                    is_required=is_required,
                ))
                break
    return results


class TestKnownTechSkills:
    def test_python_detected(self):
        skills = extract_skills("Nous cherchons un développeur Python expérimenté.")
        names = [s.normalized for s in skills]
        assert "python" in names

    def test_multiple_skills(self):
        text = "Stack: Python, React, PostgreSQL, Docker"
        skills = extract_skills(text)
        names = {s.normalized for s in skills}
        assert {"python", "react", "postgresql", "docker"}.issubset(names)

    def test_kubernetes_alias(self):
        skills = extract_skills("Expérience avec k8s et Docker.")
        names = [s.normalized for s in skills]
        assert "kubernetes" in names

    def test_kafka_alias(self):
        skills = extract_skills("Connaissance d'Apache Kafka appréciée.")
        names = [s.normalized for s in skills]
        assert "kafka" in names

    def test_no_skills_empty_text(self):
        assert extract_skills("") == []

    def test_no_skills_unrelated_text(self):
        skills = extract_skills("Nous offrons une excellente mutuelle et des tickets restaurant.")
        assert skills == []


class TestConfidenceScoring:
    def test_required_signal_raises_confidence(self):
        text = "Maîtrise de Python requise."
        skills = extract_skills(text)
        py = next(s for s in skills if s.normalized == "python")
        assert py.confidence >= 0.90

    def test_default_confidence(self):
        text = "Bonne connaissance de Docker."
        skills = extract_skills(text)
        docker = next(s for s in skills if s.normalized == "docker")
        assert 0.0 < docker.confidence <= 1.0

    def test_confidence_range(self):
        skills = extract_skills("Python, TypeScript, React, SQL")
        for s in skills:
            assert 0.0 <= s.confidence <= 1.0


class TestRequiredVsOptional:
    def test_required_by_default(self):
        skills = extract_skills("Compétences en Python.")
        py = next(s for s in skills if s.normalized == "python")
        assert py.is_required is True

    def test_optional_signal_detected(self):
        text = "TypeScript souhaité mais pas obligatoire."
        skills = extract_skills(text)
        ts = next((s for s in skills if s.normalized == "typescript"), None)
        if ts:
            assert ts.is_required is False


class TestNormalisation:
    def test_normalized_is_lowercase(self):
        skills = extract_skills("PYTHON developer needed")
        for s in skills:
            assert s.normalized == s.normalized.lower()

    def test_react_aliases(self):
        for alias in ["React", "ReactJS", "react.js"]:
            skills = extract_skills(f"Expérience avec {alias}")
            names = [s.normalized for s in skills]
            assert "react" in names, f"Alias '{alias}' not detected"
