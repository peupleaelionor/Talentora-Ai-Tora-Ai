"""
France Travail (Pôle Emploi) Emploi Store API connector.

Authenticates with the OAuth2 client-credentials flow, fetches paginated
job listings, respects per-minute rate limits, and normalises French job
data into the canonical Talentora schema.

API reference: https://francetravail.io/data/api/offres-emploi
"""

from __future__ import annotations

import asyncio
import os
import time
from datetime import datetime, timezone
from typing import Any

import httpx
import structlog
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from packages.connectors.base import BaseConnector, NormalizedJob, RawJob

log = structlog.get_logger(__name__)

# Base URL for the Emploi Store v2 API
_API_BASE = "https://api.francetravail.io/partenaire/offresdemploi/v2"
_TOKEN_URL = "https://entreprise.francetravail.fr/connexion/oauth2/access_token"
_SCOPE = "api_offresdemploiv2 o2dsoffre"

# Contract-type mapping from France Travail codes to canonical values
_CONTRACT_MAP: dict[str, str] = {
    "CDI": "CDI",
    "CDD": "CDD",
    "MIS": "interim",
    "SAI": "seasonal",
    "LIB": "freelance",
    "FRA": "franchise",
    "REP": "business_takeover",
    "TTI": "TTI",
    "DDI": "DDI",
}

# Remote / télétravail mapping
_REMOTE_MAP: dict[str, str] = {
    "fullTT": "full",
    "partielTT": "partial",
    "nonTT": "none",
    "occasionnelTT": "occasional",
}


class FranceTravailConnector(BaseConnector):
    """
    Connector for the France Travail (ex-Pôle Emploi) Emploi Store API.

    Environment variables
    ---------------------
    FT_CLIENT_ID     – OAuth2 client identifier.
    FT_CLIENT_SECRET – OAuth2 client secret.
    """

    source_id = "france_travail"
    source_name = "France Travail"
    rate_limit = 100  # requests/minute (API cap)

    _PAGE_SIZE = 150  # max allowed by the API

    def __init__(self) -> None:
        self._client_id = os.environ["FT_CLIENT_ID"]
        self._client_secret = os.environ["FT_CLIENT_SECRET"]
        self._access_token: str | None = None
        self._token_expires_at: float = 0.0
        self._http: httpx.AsyncClient = httpx.AsyncClient(timeout=30)
        self._request_times: list[float] = []

    # ------------------------------------------------------------------
    # OAuth2 token management
    # ------------------------------------------------------------------

    async def _ensure_token(self) -> str:
        """Return a valid access token, refreshing if necessary."""
        if self._access_token and time.monotonic() < self._token_expires_at - 30:
            return self._access_token

        response = await self._http.post(
            _TOKEN_URL,
            data={
                "grant_type": "client_credentials",
                "client_id": self._client_id,
                "client_secret": self._client_secret,
                "scope": _SCOPE,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        response.raise_for_status()
        payload = response.json()
        self._access_token = payload["access_token"]
        self._token_expires_at = time.monotonic() + payload.get("expires_in", 1499)
        log.debug("france_travail.token_refreshed")
        return self._access_token

    # ------------------------------------------------------------------
    # Rate limiter
    # ------------------------------------------------------------------

    async def _throttle(self) -> None:
        """Sliding-window rate limiter: max ``rate_limit`` calls per 60 s."""
        now = time.monotonic()
        self._request_times = [t for t in self._request_times if now - t < 60]
        if len(self._request_times) >= self.rate_limit:
            sleep_for = 60 - (now - self._request_times[0]) + 0.1
            log.debug("france_travail.throttle", sleep_seconds=round(sleep_for, 2))
            await asyncio.sleep(sleep_for)
        self._request_times.append(time.monotonic())

    # ------------------------------------------------------------------
    # HTTP helper with retry
    # ------------------------------------------------------------------

    @retry(
        retry=retry_if_exception_type((httpx.HTTPStatusError, httpx.TransportError)),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        stop=stop_after_attempt(5),
        reraise=True,
    )
    async def _get(self, path: str, params: dict[str, Any]) -> dict[str, Any]:
        await self._throttle()
        token = await self._ensure_token()
        url = f"{_API_BASE}{path}"

        response = await self._http.get(
            url,
            params=params,
            headers={"Authorization": f"Bearer {token}"},
        )

        if response.status_code == 429:
            retry_after = int(response.headers.get("Retry-After", "10"))
            log.warning("france_travail.rate_limited", retry_after=retry_after)
            await asyncio.sleep(retry_after)
            response.raise_for_status()

        response.raise_for_status()
        return response.json()

    # ------------------------------------------------------------------
    # BaseConnector interface
    # ------------------------------------------------------------------

    async def fetch_job_list(
        self, page: int, filters: dict[str, Any]
    ) -> list[RawJob]:
        """
        Fetch one page of job offers from the France Travail API.

        Parameters
        ----------
        page:
            1-indexed page number.
        filters:
            Supported keys: ``motsCles`` (keyword), ``departement``,
            ``commune``, ``codeROME``, ``typeContrat``, ``minCreationDate``.
        """
        start = (page - 1) * self._PAGE_SIZE
        params: dict[str, Any] = {
            "range": f"{start}-{start + self._PAGE_SIZE - 1}",
            **filters,
        }

        try:
            data = await self._get("/offres/search", params)
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 204:
                return []
            raise

        results = data.get("resultats", [])
        log.debug("france_travail.page_fetched", page=page, count=len(results))

        return [
            RawJob(
                source_id=self.source_id,
                external_id=r["id"],
                raw_data=r,
                source_url=r.get("origineOffre", {}).get("urlOrigine"),
            )
            for r in results
        ]

    async def fetch_job_detail(self, job_id: str) -> RawJob:
        """
        Fetch full detail for a single job offer.

        Parameters
        ----------
        job_id:
            France Travail offer identifier (e.g. ``"162GSKR"``).
        """
        data = await self._get(f"/offres/{job_id}", params={})
        return RawJob(
            source_id=self.source_id,
            external_id=data["id"],
            raw_data=data,
            source_url=data.get("origineOffre", {}).get("urlOrigine"),
        )

    def normalize(self, raw_job: RawJob) -> NormalizedJob:
        """
        Map a France Travail raw job payload to ``NormalizedJob``.

        Handles optional salary fields, remote indicators, and
        contract type codes.
        """
        d = raw_job.raw_data

        # Parse published date
        published_at: datetime | None = None
        if date_str := d.get("dateCreation"):
            try:
                published_at = datetime.fromisoformat(date_str).replace(tzinfo=timezone.utc)
            except ValueError:
                pass

        # Salary
        salary_data = d.get("salaire", {})
        salary_min, salary_max, currency, period = self._parse_salary(
            salary_data.get("libelle", "")
        )

        # Location
        lieu = d.get("lieuTravail", {})
        location = lieu.get("libelle", "")
        country = "FR"

        # Remote
        remote_code = d.get("typeContratLibelle", "")
        remote = _REMOTE_MAP.get(d.get("teleTravailLibelle", ""), "none")

        return NormalizedJob(
            source_id=self.source_id,
            external_id=d["id"],
            title=d.get("intitule", "").strip(),
            company=d.get("entreprise", {}).get("nom", "").strip(),
            description=d.get("description", "").strip(),
            location=location,
            country=country,
            language="fr",
            url=raw_job.source_url,
            published_at=published_at,
            contract_type=_CONTRACT_MAP.get(d.get("typeContrat", ""), d.get("typeContrat")),
            remote=remote,
            salary_min=salary_min,
            salary_max=salary_max,
            salary_currency=currency,
            salary_period=period,
            raw_id=raw_job.raw_id,
            extra={
                "rome_code": d.get("romeCode"),
                "rome_libelle": d.get("romeLibelle"),
                "naf_code": d.get("secteurActivite"),
                "experience_required": d.get("experienceExige"),
                "qualification": d.get("qualificationLibelle"),
            },
        )

    # ------------------------------------------------------------------
    # Salary parsing helpers
    # ------------------------------------------------------------------

    def _parse_salary(
        self, libelle: str
    ) -> tuple[float | None, float | None, str | None, str | None]:
        """
        Attempt to extract salary bounds from a France Travail salary label.

        France Travail salary labels have highly variable formats
        (e.g. ``"Mensuel de 2000.00 Euros à 2500.00 Euros"``).
        Falls back to ``None`` when parsing fails.
        """
        import re

        if not libelle:
            return None, None, None, None

        currency = "EUR" if "Euro" in libelle or "€" in libelle else None
        period = None
        if "Annuel" in libelle:
            period = "yearly"
        elif "Mensuel" in libelle:
            period = "monthly"
        elif "Horaire" in libelle:
            period = "hourly"
        elif "Hebdomadaire" in libelle:
            period = "weekly"

        amounts = re.findall(r"(\d[\d\s]*(?:\.\d+)?)\s*(?:Euros?|€)?", libelle)
        floats = []
        for a in amounts:
            try:
                floats.append(float(a.replace(" ", "")))
            except ValueError:
                pass

        if len(floats) >= 2:
            return min(floats), max(floats), currency, period
        if len(floats) == 1:
            return floats[0], floats[0], currency, period
        return None, None, currency, period
