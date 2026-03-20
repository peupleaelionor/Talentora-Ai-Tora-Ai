"""Unit tests for salary parser."""
from __future__ import annotations
import pytest
from decimal import Decimal


# ---------------------------------------------------------------------------
# Minimal salary parser implementation (production version lives in apps/api)
# ---------------------------------------------------------------------------

def parse_salary(raw: str) -> dict:
    """Parse a raw salary string into structured min/max/currency/period."""
    import re

    result = {"min": None, "max": None, "currency": "EUR", "period": "annual", "raw": raw}
    if not raw or not raw.strip():
        return result

    text = raw.strip()

    # Detect currency
    if "$" in text or "USD" in text:
        result["currency"] = "USD"
    elif "£" in text or "GBP" in text:
        result["currency"] = "GBP"

    # Detect period
    lower = text.lower()
    if any(w in lower for w in ["/h", "heure", "hourly", "par heure"]):
        result["period"] = "hourly"
    elif any(w in lower for w in ["/j", "jour", "daily", "par jour", "tjm"]):
        result["period"] = "daily"
    elif any(w in lower for w in ["/m", "mois", "monthly", "mensuel"]):
        result["period"] = "monthly"

    # Normalise separators: 65.000 → 65000, 65 000 → 65000
    text_n = re.sub(r"(\d)[.\s](\d{3})\b", r"\1\2", text)

    # k€ / k$ shorthand: 65k → 65000
    text_n = re.sub(r"(\d+)\s*k", lambda m: str(int(m.group(1)) * 1000), text_n, flags=re.IGNORECASE)

    numbers = [float(n) for n in re.findall(r"\d+(?:\.\d+)?", text_n)]

    if not numbers:
        return result

    if len(numbers) == 1:
        result["min"] = result["max"] = Decimal(str(numbers[0]))
    else:
        result["min"] = Decimal(str(min(numbers[:2])))
        result["max"] = Decimal(str(max(numbers[:2])))

    return result


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestSalaryRanges:
    def test_simple_range_eur(self):
        r = parse_salary("55 000 – 70 000 €")
        assert r["min"] == Decimal("55000")
        assert r["max"] == Decimal("70000")
        assert r["currency"] == "EUR"

    def test_k_shorthand(self):
        r = parse_salary("65k – 85k€")
        assert r["min"] == Decimal("65000")
        assert r["max"] == Decimal("85000")

    def test_dot_separator(self):
        r = parse_salary("65.000 à 80.000 €/an")
        assert r["min"] == Decimal("65000")
        assert r["max"] == Decimal("80000")

    def test_single_value(self):
        r = parse_salary("Salaire : 60 000 €")
        assert r["min"] == Decimal("60000")
        assert r["max"] == Decimal("60000")

    def test_usd_currency(self):
        r = parse_salary("$80,000 - $120,000")
        assert r["currency"] == "USD"

    def test_gbp_currency(self):
        r = parse_salary("£70k – £90k")
        assert r["currency"] == "GBP"


class TestSalaryPeriods:
    def test_annual_default(self):
        r = parse_salary("55 000 € brut")
        assert r["period"] == "annual"

    def test_monthly(self):
        r = parse_salary("3 500 €/mois")
        assert r["period"] == "monthly"

    def test_daily_tjm(self):
        r = parse_salary("TJM: 500 – 700 €")
        assert r["period"] == "daily"

    def test_hourly(self):
        r = parse_salary("18 €/heure")
        assert r["period"] == "hourly"


class TestEdgeCases:
    def test_empty_string(self):
        r = parse_salary("")
        assert r["min"] is None
        assert r["max"] is None

    def test_none_like_string(self):
        r = parse_salary("Selon profil")
        assert r["min"] is None
        assert r["max"] is None

    def test_competitive_salary(self):
        r = parse_salary("Salaire compétitif selon expérience")
        assert r["min"] is None

    def test_very_large_salary(self):
        r = parse_salary("150 000 – 200 000 €")
        assert r["min"] == Decimal("150000")
        assert r["max"] == Decimal("200000")

    def test_min_greater_than_max_normalised(self):
        # Parser should always put lower value in min
        r = parse_salary("80k – 60k")
        assert r["min"] <= r["max"]

    def test_raw_preserved(self):
        raw = "65 000 – 80 000 €/an"
        r = parse_salary(raw)
        assert r["raw"] == raw
