"""Unit tests for text cleaner."""
from __future__ import annotations
import re
import pytest


def clean_text(text: str) -> str:
    """Clean and normalise job description text."""
    if not text:
        return ""
    # Strip HTML tags
    text = re.sub(r"<[^>]+>", " ", text)
    # Decode common HTML entities
    replacements = {"&amp;": "&", "&lt;": "<", "&gt;": ">", "&nbsp;": " ", "&#39;": "'", "&quot;": '"'}
    for entity, char in replacements.items():
        text = text.replace(entity, char)
    # Collapse whitespace
    text = re.sub(r"\s+", " ", text)
    # Remove null bytes
    text = text.replace("\x00", "")
    # Trim
    return text.strip()


def normalize_title(title: str) -> str:
    """Normalise a job title for deduplication."""
    if not title:
        return ""
    title = title.lower().strip()
    # Remove parenthetical suffixes like (H/F), (F/H), (M/F/D)
    title = re.sub(r"\s*[\(\[](?:h/f|f/h|m/f|m/w|m/f/d|h\.f\.|f\.h\.)[\)\]]", "", title, flags=re.IGNORECASE)
    # Normalise common abbreviations
    title = re.sub(r"\bsr\.?\b", "senior", title)
    title = re.sub(r"\bjr\.?\b", "junior", title)
    title = re.sub(r"\s+", " ", title)
    return title.strip()


class TestCleanText:
    def test_strips_html_tags(self):
        assert clean_text("<p>Hello <b>World</b></p>") == "Hello World"

    def test_decodes_html_entities(self):
        assert "&amp;" not in clean_text("Tom &amp; Jerry")
        assert "Tom & Jerry" == clean_text("Tom &amp; Jerry")

    def test_collapses_whitespace(self):
        result = clean_text("Hello    World\t\nFoo")
        assert "  " not in result

    def test_empty_string(self):
        assert clean_text("") == ""

    def test_none_like(self):
        assert clean_text(None) == ""  # type: ignore[arg-type]

    def test_strips_null_bytes(self):
        assert "\x00" not in clean_text("Hello\x00World")

    def test_trims_whitespace(self):
        assert clean_text("  hello  ") == "hello"

    def test_nbsp_decoded(self):
        result = clean_text("hello&nbsp;world")
        assert "&nbsp;" not in result

    def test_nested_tags(self):
        html = "<div><ul><li>Item 1</li><li>Item 2</li></ul></div>"
        result = clean_text(html)
        assert "<" not in result
        assert "Item 1" in result
        assert "Item 2" in result


class TestNormalizeTitle:
    def test_lowercase(self):
        assert normalize_title("Senior Engineer") == "senior engineer"

    def test_removes_hf(self):
        assert "(h/f)" not in normalize_title("Développeur Python (H/F)")

    def test_removes_fh(self):
        assert "(f/h)" not in normalize_title("Data Analyst (F/H)")

    def test_sr_to_senior(self):
        assert "senior" in normalize_title("Sr. Backend Engineer")

    def test_jr_to_junior(self):
        assert "junior" in normalize_title("Jr Developer")

    def test_empty_title(self):
        assert normalize_title("") == ""

    def test_strips_whitespace(self):
        assert normalize_title("  Lead Engineer  ") == "lead engineer"

    def test_collapses_spaces(self):
        result = normalize_title("Python   Developer")
        assert "  " not in result
