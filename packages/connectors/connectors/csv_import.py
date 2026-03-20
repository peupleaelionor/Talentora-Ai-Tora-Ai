"""
CSV / JSON import connector for Talentora.

Allows bulk ingestion of job offers from local or S3-hosted CSV and
JSON files using a well-defined column/field mapping.
"""

from __future__ import annotations

import csv
import io
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import structlog

from packages.connectors.base import BaseConnector, NormalizedJob, RawJob

log = structlog.get_logger(__name__)

# Expected CSV/JSON field names mapped to NormalizedJob fields.
# Keys are canonical names; values are lists of accepted aliases.
_FIELD_MAP: dict[str, list[str]] = {
    "external_id": ["id", "job_id", "reference", "ref"],
    "title": ["title", "job_title", "poste", "intitule"],
    "company": ["company", "employer", "entreprise", "societe"],
    "description": ["description", "content", "texte", "details"],
    "location": ["location", "lieu", "city", "ville", "localisation"],
    "country": ["country", "pays", "country_code"],
    "url": ["url", "link", "lien", "source_url"],
    "published_at": ["published_at", "date", "created_at", "date_publication"],
    "contract_type": ["contract_type", "type_contrat", "contrat"],
    "remote": ["remote", "teletravail", "remote_type"],
    "salary_min": ["salary_min", "salaire_min", "min_salary"],
    "salary_max": ["salary_max", "salaire_max", "max_salary"],
    "salary_currency": ["salary_currency", "currency", "devise"],
    "salary_period": ["salary_period", "period", "periode"],
}


def _resolve(row: dict[str, Any], canonical: str) -> Any:
    """Return the first matching alias value from a row dict."""
    for alias in _FIELD_MAP.get(canonical, [canonical]):
        if alias in row:
            return row[alias]
    return None


class CsvImportConnector(BaseConnector):
    """
    Connector that ingests job offers from CSV or JSON files.

    Configuration is supplied via constructor parameters or environment
    variables (``CSV_SOURCE_PATH``, ``CSV_SOURCE_FORMAT``).

    Parameters
    ----------
    file_path:
        Absolute path or S3 URI (``s3://bucket/key``) to the source file.
    file_format:
        ``"csv"`` or ``"json"``.  Auto-detected from extension when omitted.
    delimiter:
        CSV column delimiter (default ``","``).
    """

    source_id = "csv_import"
    source_name = "CSV/JSON Import"
    rate_limit = 1000  # effectively unlimited for local files

    def __init__(
        self,
        file_path: str | None = None,
        file_format: str | None = None,
        delimiter: str = ",",
    ) -> None:
        self._file_path = file_path or os.environ.get("CSV_SOURCE_PATH", "")
        self._format = file_format or os.environ.get("CSV_SOURCE_FORMAT", "")
        self._delimiter = delimiter
        self._records: list[dict[str, Any]] = []
        self._loaded = False

    # ------------------------------------------------------------------
    # Loading helpers
    # ------------------------------------------------------------------

    def _auto_detect_format(self, path: str) -> str:
        suffix = Path(path).suffix.lower()
        if suffix in {".json", ".jsonl", ".ndjson"}:
            return "json"
        return "csv"

    def _load_from_local(self, path: str, fmt: str) -> list[dict[str, Any]]:
        with open(path, encoding="utf-8") as fh:
            if fmt == "json":
                data = json.load(fh)
                return data if isinstance(data, list) else [data]
            reader = csv.DictReader(fh, delimiter=self._delimiter)
            return list(reader)

    def _load_from_s3(self, uri: str, fmt: str) -> list[dict[str, Any]]:
        import boto3

        _, path = uri[5:].split("/", 1)
        bucket, key = path.split("/", 1)
        s3 = boto3.client("s3")
        obj = s3.get_object(Bucket=bucket, Key=key)
        content = obj["Body"].read().decode("utf-8")

        if fmt == "json":
            data = json.loads(content)
            return data if isinstance(data, list) else [data]
        reader = csv.DictReader(io.StringIO(content), delimiter=self._delimiter)
        return list(reader)

    def _ensure_loaded(self) -> None:
        if self._loaded:
            return

        path = self._file_path
        if not path:
            raise ValueError("No file path configured for CsvImportConnector")

        fmt = self._format or self._auto_detect_format(path)

        if path.startswith("s3://"):
            self._records = self._load_from_s3(path, fmt)
        else:
            self._records = self._load_from_local(path, fmt)

        self._loaded = True
        log.info("csv_import.loaded", path=path, format=fmt, count=len(self._records))

    # ------------------------------------------------------------------
    # BaseConnector interface
    # ------------------------------------------------------------------

    async def fetch_job_list(
        self, page: int, filters: dict[str, Any]
    ) -> list[RawJob]:
        """
        Return a paginated slice of records from the loaded file.

        Parameters
        ----------
        page:
            1-indexed page number.
        filters:
            Supported: ``page_size`` (default 100).
        """
        self._ensure_loaded()
        page_size: int = int(filters.get("page_size", 100))
        start = (page - 1) * page_size
        end = start + page_size
        batch = self._records[start:end]

        return [
            RawJob(
                source_id=self.source_id,
                external_id=str(_resolve(r, "external_id") or hash(json.dumps(r, sort_keys=True))),
                raw_data=dict(r),
            )
            for r in batch
        ]

    async def fetch_job_detail(self, job_id: str) -> RawJob:
        """
        Return the record matching ``job_id`` from the loaded file.
        """
        self._ensure_loaded()
        for r in self._records:
            if str(_resolve(r, "external_id")) == job_id:
                return RawJob(
                    source_id=self.source_id,
                    external_id=job_id,
                    raw_data=dict(r),
                )
        raise KeyError(f"Job {job_id!r} not found in CSV/JSON source")

    def normalize(self, raw_job: RawJob) -> NormalizedJob:
        """Map a CSV/JSON row to a canonical ``NormalizedJob``."""
        d = raw_job.raw_data

        # Parse published_at
        published_at: datetime | None = None
        if date_str := _resolve(d, "published_at"):
            try:
                published_at = datetime.fromisoformat(str(date_str)).replace(tzinfo=timezone.utc)
            except ValueError:
                pass

        # Salary
        def _float_or_none(v: Any) -> float | None:
            try:
                return float(v) if v not in (None, "", "N/A") else None
            except (TypeError, ValueError):
                return None

        return NormalizedJob(
            source_id=self.source_id,
            external_id=raw_job.external_id,
            title=str(_resolve(d, "title") or "").strip(),
            company=str(_resolve(d, "company") or "").strip(),
            description=str(_resolve(d, "description") or "").strip(),
            location=str(_resolve(d, "location") or "").strip(),
            country=str(_resolve(d, "country") or "FR").strip().upper()[:2],
            url=str(_resolve(d, "url") or "") or None,
            published_at=published_at,
            contract_type=str(_resolve(d, "contract_type") or "") or None,
            remote=str(_resolve(d, "remote") or "") or None,
            salary_min=_float_or_none(_resolve(d, "salary_min")),
            salary_max=_float_or_none(_resolve(d, "salary_max")),
            salary_currency=str(_resolve(d, "salary_currency") or "") or None,
            salary_period=str(_resolve(d, "salary_period") or "") or None,
            raw_id=raw_job.raw_id,
        )
