"""
Salary extraction module for Talentora NLP pipeline.

Parses free-form salary strings into structured min/max/currency/period
data.  Handles common European and US formats.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

import structlog

log = structlog.get_logger(__name__)

# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------


@dataclass
class SalaryInfo:
    """Structured salary information extracted from text."""

    min_value: float | None
    max_value: float | None
    currency: str | None  # ISO 4217 code e.g. "EUR", "USD", "GBP"
    period: str | None  # "yearly", "monthly", "daily", "hourly"
    confidence: float  # 0.0 – 1.0
    raw_text: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "min": self.min_value,
            "max": self.max_value,
            "currency": self.currency,
            "period": self.period,
            "confidence": self.confidence,
            "raw_text": self.raw_text,
        }


# ---------------------------------------------------------------------------
# Currency & period detection patterns
# ---------------------------------------------------------------------------

_CURRENCY_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"€|EUR|euros?", re.IGNORECASE), "EUR"),
    (re.compile(r"\$|USD|dollars?", re.IGNORECASE), "USD"),
    (re.compile(r"£|GBP|pounds?", re.IGNORECASE), "GBP"),
    (re.compile(r"CHF|francs?\s+suisses?", re.IGNORECASE), "CHF"),
]

_PERIOD_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"/?\s*an(?:nuel)?|per\s+year|yearly|p\.a\.|\/year", re.IGNORECASE), "yearly"),
    (re.compile(r"/?\s*mois|mensuel|per\s+month|monthly|\/month", re.IGNORECASE), "monthly"),
    (re.compile(r"/?\s*jour|daily|per\s+day|\/day", re.IGNORECASE), "daily"),
    (re.compile(r"/?\s*heure|hourly|per\s+hour|\/h(?:r|our)?", re.IGNORECASE), "hourly"),
]

# Multipliers to convert shorthand (e.g. "50k" -> 50000)
_MULTIPLIERS: list[tuple[re.Pattern[str], float]] = [
    (re.compile(r"(\d[\d\s,\.]*)\s*k(?:€|\$|£)?", re.IGNORECASE), 1_000),
    (re.compile(r"(\d[\d\s,\.]*)\s*m(?:€|\$|£)?", re.IGNORECASE), 1_000_000),
]

# Main salary amount capture:  one or two amounts separated by "à", "-", "to", "and", "entre"
_RANGE_PATTERN = re.compile(
    r"""
    (?:entre\s+|between\s+)?
    (?P<amount1>
        \d{1,3}(?:[\s,\.]\d{3})*(?:\.\d+)?   # 50 000 or 50,000 or 50.000
        |\d+                                   # plain integer
    )
    \s*(?:k|K)?                                # optional k-suffix
    \s*(?:€|\$|£|EUR|USD|GBP)?                 # optional inline currency
    \s*(?:à|-|–|to|and|et)\s*                 # separator
    (?P<amount2>
        \d{1,3}(?:[\s,\.]\d{3})*(?:\.\d+)?
        |\d+
    )
    \s*(?:k|K)?
    \s*(?:€|\$|£|EUR|USD|GBP)?
    """,
    re.IGNORECASE | re.VERBOSE,
)

_SINGLE_PATTERN = re.compile(
    r"""
    (?:à\s+partir\s+de|from|starting\s+at|dès\s+)?
    (?P<amount>
        \d{1,3}(?:[\s,\.]\d{3})*(?:\.\d+)?
        |\d+
    )
    \s*(?:k|K)?
    \s*(?:€|\$|£|EUR|USD|GBP)?
    """,
    re.IGNORECASE | re.VERBOSE,
)


def _clean_amount(raw: str) -> float:
    """Parse a raw amount string to float, handling European separators."""
    s = raw.replace(" ", "").replace("\u00a0", "")
    if "," in s and "." in s:
        # e.g. "50,000.00" (US) or "50.000,00" (EU)
        if s.index(",") < s.index("."):
            s = s.replace(",", "")
        else:
            s = s.replace(".", "").replace(",", ".")
    elif "," in s:
        if len(s.split(",")[-1]) <= 2:
            s = s.replace(",", ".")
        else:
            s = s.replace(",", "")
    elif "." in s:
        if len(s.split(".")[-1]) > 2:
            s = s.replace(".", "")
    return float(s)


def _apply_k_suffix(raw_text: str, value: float) -> float:
    """Apply 'k' multiplier when present immediately after the digits."""
    if re.search(r"\d\s*k\b", raw_text, re.IGNORECASE):
        return value * 1_000
    return value


def _detect_currency(text: str) -> str | None:
    for pattern, code in _CURRENCY_PATTERNS:
        if pattern.search(text):
            return code
    return None


def _detect_period(text: str) -> str | None:
    for pattern, period in _PERIOD_PATTERNS:
        if pattern.search(text):
            return period
    return None


# ---------------------------------------------------------------------------
# Salary parser
# ---------------------------------------------------------------------------


class SalaryParser:
    """
    Extract structured salary information from free-form text.

    Handles formats including:
    - ``"50k€"``
    - ``"50 000 € / an"``
    - ``"$80,000 - $100,000"``
    - ``"entre 45 et 55k"``
    - ``"à partir de 3 000 € / mois"``
    """

    def extract_salary(self, text: str) -> SalaryInfo | None:
        """
        Extract salary from ``text``.

        Parameters
        ----------
        text:
            Job description or salary field text.

        Returns
        -------
        :class:`SalaryInfo` if salary data is found, otherwise ``None``.
        """
        if not text:
            return None

        currency = _detect_currency(text)
        period = _detect_period(text)

        # Try range match first (higher confidence)
        range_match = _RANGE_PATTERN.search(text)
        if range_match:
            try:
                a1_raw = range_match.group("amount1")
                a2_raw = range_match.group("amount2")
                a1 = _clean_amount(a1_raw)
                a2 = _clean_amount(a2_raw)

                # Extract the substring around the match to check for 'k'
                snippet = range_match.group(0)
                a1 = _apply_k_suffix(snippet.split(re.split(r"à|-|–|to|and|et", snippet)[0])[0], a1)
                a2 = _apply_k_suffix(snippet, a2)

                salary = SalaryInfo(
                    min_value=min(a1, a2),
                    max_value=max(a1, a2),
                    currency=currency or "EUR",
                    period=period or "yearly",
                    confidence=0.90,
                    raw_text=snippet,
                )
                log.debug("salary_parser.range_found", min=salary.min_value, max=salary.max_value)
                return salary
            except (ValueError, AttributeError):
                pass

        # Single amount fallback
        single_match = _SINGLE_PATTERN.search(text)
        if single_match:
            try:
                a_raw = single_match.group("amount")
                a = _clean_amount(a_raw)
                snippet = single_match.group(0)
                a = _apply_k_suffix(snippet, a)

                # Plausibility check: ignore very small / very large values
                if not (500 <= a <= 10_000_000):
                    return None

                salary = SalaryInfo(
                    min_value=a,
                    max_value=None,
                    currency=currency or "EUR",
                    period=period or "yearly",
                    confidence=0.65,
                    raw_text=snippet,
                )
                log.debug("salary_parser.single_found", amount=a)
                return salary
            except (ValueError, AttributeError):
                pass

        return None
