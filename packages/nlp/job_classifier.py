"""
Job classification module for Talentora NLP pipeline.

Classifies job titles and descriptions into canonical roles, seniority
levels, and industry sectors using rule-based heuristics and keyword
matching suitable for the European/French job market.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

import structlog

log = structlog.get_logger(__name__)

# ---------------------------------------------------------------------------
# Taxonomy
# ---------------------------------------------------------------------------

# canonical_role -> (list of title keywords, confidence)
ROLE_TAXONOMY: dict[str, tuple[list[str], float]] = {
    "software_engineer": (
        ["développeur", "developer", "software engineer", "ingénieur logiciel",
         "backend", "frontend", "fullstack", "full-stack", "full stack"],
        0.85,
    ),
    "data_scientist": (
        ["data scientist", "machine learning engineer", "ml engineer",
         "deep learning", "data science"],
        0.90,
    ),
    "data_engineer": (
        ["data engineer", "ingénieur data", "data pipeline", "etl engineer"],
        0.88,
    ),
    "data_analyst": (
        ["data analyst", "analyste de données", "business analyst", "bi analyst",
         "reporting analyst"],
        0.85,
    ),
    "devops_engineer": (
        ["devops", "sre", "site reliability", "platform engineer",
         "infrastructure engineer", "cloud engineer"],
        0.88,
    ),
    "product_manager": (
        ["product manager", "chef de produit", "product owner", "po "],
        0.87,
    ),
    "designer": (
        ["ux designer", "ui designer", "product designer", "graphiste",
         "web designer", "ux/ui"],
        0.85,
    ),
    "project_manager": (
        ["project manager", "chef de projet", "programme manager",
         "delivery manager", "scrum master"],
        0.83,
    ),
    "security_engineer": (
        ["security engineer", "cybersecurity", "pentester", "soc analyst",
         "ingénieur sécurité"],
        0.90,
    ),
    "qa_engineer": (
        ["qa", "quality assurance", "test engineer", "ingénieur test",
         "tester", "testeur"],
        0.85,
    ),
    "sales": (
        ["account executive", "sales engineer", "business developer",
         "commercial", "ingénieur commercial", "account manager"],
        0.82,
    ),
    "marketing": (
        ["marketing manager", "growth hacker", "seo specialist",
         "content manager", "digital marketing"],
        0.82,
    ),
    "hr": (
        ["rh", "human resources", "recruiter", "recruteur",
         "talent acquisition", "people operations"],
        0.80,
    ),
}

# Seniority keywords (checked in title + description)
SENIORITY_TAXONOMY: dict[str, tuple[list[str], float]] = {
    "intern": (["stagiaire", "intern", "stage", "alternant", "alternance", "apprenti"], 0.92),
    "junior": (["junior", "débutant", "entry level", "0-2 ans", "0-3 ans"], 0.88),
    "mid": (["confirmé", "expérimenté", "2-5 ans", "3-5 ans", "mid-level", "mid level"], 0.82),
    "senior": (["senior", "expérimenté", "5+ ans", "10+ ans", "lead", "référent"], 0.85),
    "lead": (["lead", "tech lead", "principal", "staff engineer", "head of"], 0.88),
    "manager": (["manager", "directeur", "director", "vp ", "head of", "cto", "cpo"], 0.90),
}

# Industry keywords (checked in description + company)
INDUSTRY_TAXONOMY: dict[str, tuple[list[str], float]] = {
    "fintech": (["banque", "finance", "fintech", "assurance", "payment", "trading"], 0.80),
    "healthtech": (["santé", "health", "médical", "pharma", "biotech", "medtech"], 0.80),
    "ecommerce": (["e-commerce", "ecommerce", "retail", "marketplace"], 0.78),
    "saas": (["saas", "b2b software", "logiciel", "plateforme"], 0.75),
    "media": (["media", "publishing", "editorial", "press", "presse"], 0.78),
    "consulting": (["consulting", "conseil", "audit", "advisory"], 0.78),
    "automotive": (["automobile", "automotive", "voiture", "mobilité"], 0.80),
    "gaming": (["gaming", "jeux vidéo", "game developer", "studio"], 0.82),
    "telecom": (["télécoms", "telecom", "operateur", "réseau", "network"], 0.80),
    "public_sector": (["secteur public", "administration", "collectivité", "ministère"], 0.82),
    "logistics": (["logistique", "supply chain", "transport", "livraison"], 0.80),
    "energy": (["énergie", "energy", "cleantech", "renouvelable", "oil"], 0.80),
}


def _best_match(
    text: str,
    taxonomy: dict[str, tuple[list[str], float]],
) -> tuple[str, float]:
    """
    Return the best-matching category and confidence for ``text``.

    Parameters
    ----------
    text:
        Lower-cased input string.
    taxonomy:
        Mapping of label -> (keywords, base_confidence).

    Returns
    -------
    Tuple of ``(label, confidence)``.  Falls back to ``("unknown", 0.0)``.
    """
    best_label = "unknown"
    best_score = 0.0

    for label, (keywords, base_conf) in taxonomy.items():
        matches = sum(1 for kw in keywords if kw.lower() in text)
        if matches > 0:
            score = min(1.0, base_conf + 0.02 * (matches - 1))
            if score > best_score:
                best_score = score
                best_label = label

    return best_label, best_score


# ---------------------------------------------------------------------------
# Classifier
# ---------------------------------------------------------------------------


class JobClassifier:
    """
    Classify job titles into canonical roles, seniority levels, and industries.

    All methods are stateless and safe to call concurrently.
    """

    def classify_title(self, title: str) -> tuple[str, float]:
        """
        Map a raw job title to a canonical role.

        Parameters
        ----------
        title:
            Raw job title string.

        Returns
        -------
        ``(canonical_role, confidence)`` tuple.
        """
        label, confidence = _best_match(title.lower(), ROLE_TAXONOMY)
        log.debug("classify_title", title=title, role=label, confidence=confidence)
        return label, confidence

    def classify_seniority(self, title: str, description: str = "") -> tuple[str, float]:
        """
        Infer the seniority level from title and description.

        Parameters
        ----------
        title:
            Raw job title.
        description:
            Job description (plain text).

        Returns
        -------
        ``(seniority_level, confidence)`` tuple.
        Possible levels: ``"intern"``, ``"junior"``, ``"mid"``,
        ``"senior"``, ``"lead"``, ``"manager"``, ``"unknown"``.
        """
        combined = f"{title} {description[:500]}".lower()
        label, confidence = _best_match(combined, SENIORITY_TAXONOMY)
        log.debug("classify_seniority", level=label, confidence=confidence)
        return label, confidence

    def classify_industry(self, description: str, company: str = "") -> tuple[str, float]:
        """
        Infer the industry sector from description and company name.

        Parameters
        ----------
        description:
            Job description text (plain text).
        company:
            Company name or brief description.

        Returns
        -------
        ``(industry, confidence)`` tuple.
        """
        combined = f"{company} {description[:1000]}".lower()
        label, confidence = _best_match(combined, INDUSTRY_TAXONOMY)
        log.debug("classify_industry", industry=label, confidence=confidence)
        return label, confidence
