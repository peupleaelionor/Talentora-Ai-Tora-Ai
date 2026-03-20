"""
Text cleaning and language detection utilities for Talentora NLP pipeline.

Provides HTML stripping, PII removal, whitespace normalisation, and
language detection backed by ``langdetect``.
"""

from __future__ import annotations

import re
from typing import Any

import structlog
from bs4 import BeautifulSoup

log = structlog.get_logger(__name__)

# ---------------------------------------------------------------------------
# PII patterns
# ---------------------------------------------------------------------------

_PII_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    # Email addresses
    (re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"), "[EMAIL]"),
    # French mobile / landline numbers
    (re.compile(r"\b(?:\+33|0)[\s.\-]?[1-9](?:[\s.\-]?\d{2}){4}\b"), "[PHONE]"),
    # Generic international phone numbers
    (re.compile(r"\+?\d[\d\s\-().]{7,14}\d"), "[PHONE]"),
    # French social security numbers (NIR)
    (re.compile(r"\b[12]\s?\d{2}\s?\d{2}\s?\d{2}\s?\d{3}\s?\d{3}\s?\d{2}\b"), "[SSN]"),
    # Postal / street addresses – simplified heuristic
    (re.compile(r"\d{1,4}\s+(?:rue|avenue|boulevard|chemin|allée|impasse|place)\b.{0,50}",
                re.IGNORECASE), "[ADDRESS]"),
    # IP addresses
    (re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"), "[IP]"),
]

# Tags whose text content should be entirely dropped (scripts, styles, nav)
_DROP_TAGS = {"script", "style", "nav", "footer", "header", "aside", "noscript"}

# Excess whitespace patterns
_MULTI_NEWLINE = re.compile(r"\n{3,}")
_MULTI_SPACE = re.compile(r" {2,}")
_LEADING_TRAILING_WS = re.compile(r"^\s+|\s+$", re.MULTILINE)


class TextCleaner:
    """
    Utility class for text sanitisation and language detection.

    All methods are stateless and safe for concurrent use.
    """

    # ------------------------------------------------------------------
    # HTML cleaning
    # ------------------------------------------------------------------

    def clean_html(self, html: str) -> str:
        """
        Strip HTML markup and return plain text.

        Drops ``<script>``, ``<style>``, and navigational elements.
        Preserves paragraph structure by converting block-level tags
        to newlines before stripping.

        Parameters
        ----------
        html:
            Raw HTML string (may also be plain text — handled gracefully).

        Returns
        -------
        Plain-text string.
        """
        if not html:
            return ""

        # Fast path: no HTML tags
        if "<" not in html:
            return self.normalize_whitespace(html)

        soup = BeautifulSoup(html, "lxml")

        # Remove unwanted tags entirely
        for tag in soup.find_all(_DROP_TAGS):
            tag.decompose()

        # Replace block elements with newlines to preserve readability
        for tag in soup.find_all(["p", "br", "li", "div", "h1", "h2", "h3", "h4", "h5", "h6"]):
            tag.insert_before("\n")
            tag.insert_after("\n")

        text = soup.get_text(separator=" ")
        return self.normalize_whitespace(text)

    # ------------------------------------------------------------------
    # PII removal
    # ------------------------------------------------------------------

    def remove_pii(self, text: str) -> str:
        """
        Replace personally identifiable information with placeholder tokens.

        Covers email addresses, French/international phone numbers,
        French NIR social security numbers, street addresses, and IPs.

        Parameters
        ----------
        text:
            Plain-text input (HTML should be stripped first).

        Returns
        -------
        Text with PII replaced by tokens such as ``[EMAIL]``, ``[PHONE]``.
        """
        for pattern, replacement in _PII_PATTERNS:
            text = pattern.sub(replacement, text)
        return text

    # ------------------------------------------------------------------
    # Whitespace normalisation
    # ------------------------------------------------------------------

    def normalize_whitespace(self, text: str) -> str:
        """
        Collapse redundant whitespace and trim lines.

        Parameters
        ----------
        text:
            Input string.

        Returns
        -------
        String with single spaces within lines and at most two
        consecutive newlines.
        """
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        text = _MULTI_SPACE.sub(" ", text)
        text = _LEADING_TRAILING_WS.sub("", text)
        text = _MULTI_NEWLINE.sub("\n\n", text)
        return text.strip()

    # ------------------------------------------------------------------
    # Language detection
    # ------------------------------------------------------------------

    def detect_language(self, text: str) -> tuple[str, float]:
        """
        Detect the dominant language of ``text``.

        Uses ``langdetect`` with a deterministic seed for reproducibility.

        Parameters
        ----------
        text:
            Plain-text content (at least ~50 characters recommended).

        Returns
        -------
        Tuple of ``(language_code, confidence)`` where ``language_code``
        is an ISO 639-1 code (e.g. ``"fr"``, ``"en"``) and ``confidence``
        is a float in ``[0, 1]``.  Returns ``("unknown", 0.0)`` on error.
        """
        if not text or len(text.strip()) < 20:
            return "unknown", 0.0

        try:
            from langdetect import detect_langs
            from langdetect import DetectorFactory

            DetectorFactory.seed = 42  # deterministic results
            results = detect_langs(text[:5_000])  # cap for performance

            if results:
                top = results[0]
                log.debug("detect_language", lang=top.lang, prob=round(top.prob, 3))
                return top.lang, round(top.prob, 3)
        except Exception as exc:
            log.warning("detect_language.error", error=str(exc))

        return "unknown", 0.0
