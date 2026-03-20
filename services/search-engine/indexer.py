"""
Search indexing service for Talentora.

Generates dense vector embeddings for job offers and maintains a
vector index (backed by a configurable provider such as pgvector,
Qdrant, or Pinecone) to power semantic similarity search.
"""

from __future__ import annotations

import os
from typing import Any

import structlog

log = structlog.get_logger(__name__)

# Embedding dimension for the configured model
_DEFAULT_DIM = 384  # all-MiniLM-L6-v2 output size

# Environment-driven backend: "memory" | "pgvector" | "qdrant" | "pinecone"
_BACKEND = os.environ.get("SEARCH_BACKEND", "memory").lower()


class SearchIndexer:
    """
    Generate and store vector embeddings for job offers.

    Supports multiple vector-store backends selected via the
    ``SEARCH_BACKEND`` environment variable.

    Parameters
    ----------
    model_name:
        Sentence-transformer model name.  Defaults to
        ``"sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"``
        which supports French and English.
    """

    def __init__(
        self,
        model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
    ) -> None:
        self._model_name = model_name
        self._model: Any = None  # lazy-loaded
        self._memory_store: dict[str, list[float]] = {}  # fallback in-process store

    # ------------------------------------------------------------------
    # Embedding generation
    # ------------------------------------------------------------------

    def _load_model(self) -> Any:
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer

                self._model = SentenceTransformer(self._model_name)
                log.info("search_indexer.model_loaded", model=self._model_name)
            except ImportError:
                log.warning(
                    "search_indexer.sentence_transformers_unavailable",
                    model=self._model_name,
                )
                self._model = None
        return self._model

    def embed(self, text: str) -> list[float]:
        """
        Generate a dense vector embedding for ``text``.

        Falls back to a zero vector when the sentence-transformers
        package is unavailable.

        Parameters
        ----------
        text:
            Plain-text content (title + skills + description).

        Returns
        -------
        List of floats with length equal to the model's output dimension.
        """
        model = self._load_model()
        if model is None:
            return [0.0] * _DEFAULT_DIM

        embedding = model.encode(text[:2048], normalize_embeddings=True)
        return embedding.tolist()

    # ------------------------------------------------------------------
    # Upsert / query
    # ------------------------------------------------------------------

    def upsert(self, job_id: str, embedding: list[float]) -> None:
        """
        Store or update the embedding for a job offer.

        Delegates to the configured backend.

        Parameters
        ----------
        job_id:
            UUID of the normalized job offer.
        embedding:
            Dense vector to store.
        """
        log.debug("search_indexer.upsert", job_id=job_id, dim=len(embedding), backend=_BACKEND)

        if _BACKEND == "memory":
            self._memory_store[job_id] = embedding

        elif _BACKEND == "pgvector":
            self._upsert_pgvector(job_id, embedding)

        elif _BACKEND == "qdrant":
            self._upsert_qdrant(job_id, embedding)

        elif _BACKEND == "pinecone":
            self._upsert_pinecone(job_id, embedding)

        else:
            log.warning("search_indexer.unknown_backend", backend=_BACKEND)
            self._memory_store[job_id] = embedding

    def search(
        self,
        query: str,
        top_k: int = 10,
        filters: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """
        Semantic search: find the most similar job offers.

        Parameters
        ----------
        query:
            Free-text search query.
        top_k:
            Number of results to return.
        filters:
            Optional metadata filters (e.g. region, contract_type).

        Returns
        -------
        List of dicts with ``job_id`` and ``score`` keys.
        """
        query_embedding = self.embed(query)

        if _BACKEND == "memory":
            return self._search_memory(query_embedding, top_k)
        if _BACKEND == "pgvector":
            return self._search_pgvector(query_embedding, top_k, filters)
        if _BACKEND == "qdrant":
            return self._search_qdrant(query_embedding, top_k, filters)
        if _BACKEND == "pinecone":
            return self._search_pinecone(query_embedding, top_k, filters)

        return []

    # ------------------------------------------------------------------
    # Backend implementations
    # ------------------------------------------------------------------

    def _upsert_pgvector(self, job_id: str, embedding: list[float]) -> None:
        try:
            from services.ingestion.pipeline import JobRepository

            repo = JobRepository()
            repo.upsert_embedding(job_id, embedding)
        except Exception as exc:
            log.error("search_indexer.pgvector_upsert_failed", job_id=job_id, error=str(exc))

    def _upsert_qdrant(self, job_id: str, embedding: list[float]) -> None:
        try:
            from qdrant_client import QdrantClient
            from qdrant_client.models import PointStruct

            client = QdrantClient(url=os.environ.get("QDRANT_URL", "http://localhost:6333"))
            client.upsert(
                collection_name="talentora_jobs",
                points=[PointStruct(id=job_id, vector=embedding)],
            )
        except Exception as exc:
            log.error("search_indexer.qdrant_upsert_failed", job_id=job_id, error=str(exc))

    def _upsert_pinecone(self, job_id: str, embedding: list[float]) -> None:
        try:
            import pinecone

            index = pinecone.Index(os.environ["PINECONE_INDEX"])
            index.upsert(vectors=[(job_id, embedding)])
        except Exception as exc:
            log.error("search_indexer.pinecone_upsert_failed", job_id=job_id, error=str(exc))

    def _search_memory(
        self, query_vec: list[float], top_k: int
    ) -> list[dict[str, Any]]:
        """Brute-force cosine similarity over in-memory store."""
        import math

        def cosine(a: list[float], b: list[float]) -> float:
            dot = sum(x * y for x, y in zip(a, b))
            norm_a = math.sqrt(sum(x * x for x in a))
            norm_b = math.sqrt(sum(x * x for x in b))
            return dot / (norm_a * norm_b) if norm_a and norm_b else 0.0

        scores = [
            {"job_id": jid, "score": cosine(query_vec, vec)}
            for jid, vec in self._memory_store.items()
        ]
        scores.sort(key=lambda s: s["score"], reverse=True)
        return scores[:top_k]

    def _search_pgvector(
        self,
        query_vec: list[float],
        top_k: int,
        filters: dict[str, Any] | None,
    ) -> list[dict[str, Any]]:
        try:
            from services.ingestion.pipeline import JobRepository

            repo = JobRepository()
            return repo.vector_search(query_vec, top_k, filters)
        except Exception as exc:
            log.error("search_indexer.pgvector_search_failed", error=str(exc))
            return []

    def _search_qdrant(
        self,
        query_vec: list[float],
        top_k: int,
        filters: dict[str, Any] | None,
    ) -> list[dict[str, Any]]:
        try:
            from qdrant_client import QdrantClient

            client = QdrantClient(url=os.environ.get("QDRANT_URL", "http://localhost:6333"))
            hits = client.search(
                collection_name="talentora_jobs",
                query_vector=query_vec,
                limit=top_k,
            )
            return [{"job_id": str(h.id), "score": h.score} for h in hits]
        except Exception as exc:
            log.error("search_indexer.qdrant_search_failed", error=str(exc))
            return []

    def _search_pinecone(
        self,
        query_vec: list[float],
        top_k: int,
        filters: dict[str, Any] | None,
    ) -> list[dict[str, Any]]:
        try:
            import pinecone

            index = pinecone.Index(os.environ["PINECONE_INDEX"])
            result = index.query(vector=query_vec, top_k=top_k, filter=filters)
            return [{"job_id": m["id"], "score": m["score"]} for m in result.get("matches", [])]
        except Exception as exc:
            log.error("search_indexer.pinecone_search_failed", error=str(exc))
            return []
