# Data Source Connectors

## France Travail API

The primary data source. Provides access to all job offers published on pole-emploi.fr.

**Registration**: https://francetravail.io/produits-api  
**Auth**: OAuth2 client credentials (`/connexion/oauth2/access_token`)  
**Rate limit**: ~2,000 calls/minute  
**Key endpoint**: `GET /partenaire/offresdemploi/v2/offres/search`

### Parameters used
| Param | Description |
|-------|-------------|
| `typeContrat` | CDI, CDD, MIS, etc. |
| `codeROME` | ROME occupation code |
| `commune` | INSEE city code |
| `range` | Pagination (0-149) |
| `minCreationDate` | Incremental ingestion |

### Connector implementation
Located at `apps/worker/connectors/france_travail.py`. Uses `httpx` async client with token caching in Redis.

---

## Connector Interface Specification

All connectors must implement the following abstract base class:

```python
from abc import ABC, abstractmethod
from typing import AsyncIterator
from dataclasses import dataclass

@dataclass
class RawJobOffer:
    source: str
    source_id: str
    source_url: str | None
    raw_data: dict

class BaseConnector(ABC):

    @property
    @abstractmethod
    def source_name(self) -> str:
        """Unique connector identifier, e.g. 'france_travail'."""

    @abstractmethod
    async def fetch(self, **kwargs) -> AsyncIterator[RawJobOffer]:
        """Yield raw job offers from the source."""

    @abstractmethod
    async def health_check(self) -> bool:
        """Return True if the source is reachable."""
```

### Adding a new connector

1. Create `apps/worker/connectors/<source_name>.py`
2. Implement `BaseConnector`
3. Register in `apps/worker/connectors/__init__.py`
4. Add credentials to `.env.example`
5. Create a Celery beat task in `apps/worker/tasks/ingestion.py`
6. Add integration test in `tests/integration/`

### Example connector skeleton

```python
class IndeedConnector(BaseConnector):
    source_name = "indeed"

    async def fetch(self, **kwargs):
        async with httpx.AsyncClient() as client:
            # paginate through results
            for page in range(MAX_PAGES):
                resp = await client.get(API_URL, params={...})
                for item in resp.json()["results"]:
                    yield RawJobOffer(
                        source=self.source_name,
                        source_id=item["id"],
                        source_url=item["url"],
                        raw_data=item,
                    )
```

### Normalisation pipeline
After ingestion, every `RawJobOffer` passes through `apps/worker/normaliser.py`:
1. Title normalisation (case, punctuation)
2. Salary parsing
3. Location geocoding
4. Contract type mapping
5. NLP skill extraction
