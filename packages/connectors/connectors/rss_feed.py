"""
RSS / Atom feed connector for Talentora.

Parses standard job-board RSS/Atom feeds using ``httpx`` for fetching
and ``beautifulsoup4`` / ``lxml`` for XML parsing.  Designed to work
with common job-board feeds (LinkedIn, Indeed, APEC, Welcome to the
Jungle, etc.).
"""

from __future__ import annotations

import asyncio
import os
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import Any
from urllib.parse import urlparse

import httpx
import structlog
from bs4 import BeautifulSoup
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from packages.connectors.base import BaseConnector, NormalizedJob, RawJob

log = structlog.get_logger(__name__)


class RssFeedConnector(BaseConnector):
    """
    Generic RSS / Atom feed connector.

    Fetches and parses a remote feed URL, extracting standard job-listing
    fields.  Subclass and override ``_extract_fields`` to customise
    field extraction for non-standard feeds.

    Parameters
    ----------
    feed_url:
        Full URL of the RSS or Atom feed.
    source_id:
        Unique identifier for this feed source (overrides class attribute).
    source_name:
        Human-readable display name.
    country:
        ISO 3166-1 alpha-2 default country for jobs in this feed.
    """

    source_id = "rss_feed"
    source_name = "RSS Feed"
    rate_limit = 30  # most feeds prefer low polling frequency

    def __init__(
        self,
        feed_url: str | None = None,
        source_id: str | None = None,
        source_name: str | None = None,
        country: str = "FR",
    ) -> None:
        self._feed_url = feed_url or os.environ.get("RSS_FEED_URL", "")
        if source_id:
            self.source_id = source_id
        if source_name:
            self.source_name = source_name
        self._country = country
        self._http = httpx.AsyncClient(
            timeout=30,
            headers={"User-Agent": "Talentora-Bot/1.0 (+https://talentora.ai/bot)"},
        )
        self._items_cache: list[dict[str, Any]] | None = None

    # ------------------------------------------------------------------
    # Feed fetching
    # ------------------------------------------------------------------

    @retry(
        retry=retry_if_exception_type((httpx.HTTPStatusError, httpx.TransportError)),
        wait=wait_exponential(multiplier=1, min=2, max=60),
        stop=stop_after_attempt(4),
        reraise=True,
    )
    async def _fetch_feed(self) -> str:
        """Download the raw feed XML."""
        if not self._feed_url:
            raise ValueError("No RSS feed URL configured")

        response = await self._http.get(self._feed_url)

        if response.status_code == 429:
            retry_after = int(response.headers.get("Retry-After", "30"))
            log.warning("rss_feed.rate_limited", retry_after=retry_after)
            await asyncio.sleep(retry_after)
            response.raise_for_status()

        response.raise_for_status()
        log.debug("rss_feed.fetched", url=self._feed_url, bytes=len(response.content))
        return response.text

    async def _parse_feed(self) -> list[dict[str, Any]]:
        """Parse the feed XML and return a list of raw item dicts."""
        if self._items_cache is not None:
            return self._items_cache

        xml = await self._fetch_feed()
        soup = BeautifulSoup(xml, "xml")

        # Support both RSS <item> and Atom <entry>
        items = soup.find_all("item") or soup.find_all("entry")

        parsed: list[dict[str, Any]] = []
        for item in items:
            parsed.append(self._extract_fields(item))

        self._items_cache = parsed
        log.info("rss_feed.parsed", count=len(parsed), url=self._feed_url)
        return parsed

    # ------------------------------------------------------------------
    # Field extraction (override in subclasses for custom feeds)
    # ------------------------------------------------------------------

    def _extract_fields(self, item: Any) -> dict[str, Any]:
        """
        Extract fields from a single RSS ``<item>`` or Atom ``<entry>`` tag.

        Parameters
        ----------
        item:
            BeautifulSoup ``Tag`` representing a single feed entry.

        Returns
        -------
        dict of raw field values.
        """

        def _text(tag_name: str) -> str:
            tag = item.find(tag_name)
            return tag.get_text(strip=True) if tag else ""

        # Unique ID: prefer <guid> / <id>, fall back to <link>
        guid = _text("guid") or _text("id") or _text("link")

        # Published date
        pub_date_raw = _text("pubDate") or _text("published") or _text("updated")
        published_at: datetime | None = None
        if pub_date_raw:
            try:
                published_at = parsedate_to_datetime(pub_date_raw)
            except Exception:
                try:
                    published_at = datetime.fromisoformat(pub_date_raw)
                except Exception:
                    pass

        # Description / summary
        description = _text("description") or _text("summary") or _text("content")

        # Categories / tags
        categories = [c.get_text(strip=True) for c in item.find_all("category")]

        return {
            "id": guid,
            "title": _text("title"),
            "link": _text("link"),
            "description": description,
            "published_at": published_at.isoformat() if published_at else None,
            "author": _text("author") or _text("dc:creator"),
            "categories": categories,
            "location": _text("location") or _text("job:location"),
            "company": _text("company") or _text("job:company"),
            "contract_type": _text("contractType") or _text("job:type"),
        }

    # ------------------------------------------------------------------
    # BaseConnector interface
    # ------------------------------------------------------------------

    async def fetch_job_list(
        self, page: int, filters: dict[str, Any]
    ) -> list[RawJob]:
        """
        Return a paginated slice of feed items.

        Parameters
        ----------
        page:
            1-indexed page number.
        filters:
            Supported: ``page_size`` (default 50).
        """
        all_items = await self._parse_feed()
        page_size: int = int(filters.get("page_size", 50))
        start = (page - 1) * page_size
        end = start + page_size
        batch = all_items[start:end]

        return [
            RawJob(
                source_id=self.source_id,
                external_id=str(item.get("id") or hash(str(item))),
                raw_data=item,
                source_url=item.get("link"),
            )
            for item in batch
        ]

    async def fetch_job_detail(self, job_id: str) -> RawJob:
        """
        Return the feed item matching ``job_id``.

        RSS feeds do not support individual job detail endpoints; this
        method searches the cached item list.
        """
        all_items = await self._parse_feed()
        for item in all_items:
            if str(item.get("id")) == job_id:
                return RawJob(
                    source_id=self.source_id,
                    external_id=job_id,
                    raw_data=item,
                    source_url=item.get("link"),
                )
        raise KeyError(f"RSS item {job_id!r} not found")

    def normalize(self, raw_job: RawJob) -> NormalizedJob:
        """Map a parsed RSS item to a canonical ``NormalizedJob``."""
        d = raw_job.raw_data

        published_at: datetime | None = None
        if date_str := d.get("published_at"):
            try:
                published_at = datetime.fromisoformat(date_str).replace(tzinfo=timezone.utc)
            except ValueError:
                pass

        return NormalizedJob(
            source_id=self.source_id,
            external_id=raw_job.external_id,
            title=str(d.get("title") or "").strip(),
            company=str(d.get("company") or "").strip(),
            description=str(d.get("description") or "").strip(),
            location=str(d.get("location") or "").strip(),
            country=self._country,
            url=raw_job.source_url,
            published_at=published_at,
            contract_type=str(d.get("contract_type") or "") or None,
            raw_id=raw_job.raw_id,
            extra={"categories": d.get("categories", [])},
        )
