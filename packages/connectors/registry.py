"""
Connector registry mapping source IDs to connector classes.

Connectors can be registered either declaratively (via ``REGISTRY``) or
dynamically at runtime (via ``ConnectorRegistry.register``).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from packages.connectors.base import BaseConnector

from packages.connectors.connectors.france_travail import FranceTravailConnector
from packages.connectors.connectors.csv_import import CsvImportConnector
from packages.connectors.connectors.rss_feed import RssFeedConnector

# ---------------------------------------------------------------------------
# Static registry  (source_id -> connector class)
# ---------------------------------------------------------------------------

REGISTRY: dict[str, type[BaseConnector]] = {
    FranceTravailConnector.source_id: FranceTravailConnector,
    CsvImportConnector.source_id: CsvImportConnector,
    RssFeedConnector.source_id: RssFeedConnector,
}


class ConnectorRegistry:
    """
    Global registry for source connectors.

    Provides class-level methods to look up, register, and enumerate
    connectors without instantiating them.
    """

    _registry: dict[str, type[BaseConnector]] = dict(REGISTRY)

    @classmethod
    def register(cls, connector_class: type[BaseConnector]) -> None:
        """
        Register a connector class under its ``source_id``.

        Parameters
        ----------
        connector_class:
            A class that subclasses :class:`BaseConnector` and declares
            a ``source_id`` class attribute.
        """
        cls._registry[connector_class.source_id] = connector_class

    @classmethod
    def get(cls, source_id: str) -> BaseConnector:
        """
        Instantiate and return the connector for ``source_id``.

        Parameters
        ----------
        source_id:
            Registry key (e.g. ``"france_travail"``).

        Returns
        -------
        Instantiated connector.

        Raises
        ------
        KeyError
            When ``source_id`` is not registered.
        """
        if source_id not in cls._registry:
            raise KeyError(
                f"Unknown source_id {source_id!r}. "
                f"Registered sources: {sorted(cls._registry)}"
            )
        return cls._registry[source_id]()

    @classmethod
    def list_sources(cls) -> list[str]:
        """Return a sorted list of all registered source IDs."""
        return sorted(cls._registry.keys())

    @classmethod
    def all_connectors(cls) -> dict[str, type[BaseConnector]]:
        """Return a copy of the current registry mapping."""
        return dict(cls._registry)
