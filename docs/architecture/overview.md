# System Architecture Overview

## C4 Model Description

### Level 1 – System Context

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              TALENTORA AI                                   │
│                   European Job Market Intelligence Platform                  │
└─────────────────────────────────────────────────────────────────────────────┘

  External Users:
  ┌─────────────┐    ┌─────────────┐    ┌──────────────────┐
  │  HR Analyst  │    │  Recruiter  │    │  API Consumer    │
  │  (browser)   │    │  (browser)  │    │  (programmatic)  │
  └──────┬───────┘    └──────┬──────┘    └────────┬─────────┘
         │                   │                    │
         └───────────────────▼────────────────────┘
                             │ HTTPS / REST
                    ┌────────▼────────┐
                    │  Talentora AI   │
                    │  (this system)  │
                    └────────┬────────┘
                             │
         ┌───────────────────┼───────────────────┐
         │                   │                   │
  ┌──────▼──────┐   ┌────────▼────────┐  ┌──────▼──────┐
  │France Travail│  │  Stripe Billing  │  │  AWS S3     │
  │  (job data)  │  │  (payments)      │  │  (storage)  │
  └─────────────┘   └─────────────────┘  └─────────────┘
```

### Level 2 – Container Diagram

```
                    ┌───────────────────────────────────────────────────────┐
                    │                    Talentora AI                        │
                    │                                                        │
  Browser ─────────►│  ┌──────────────┐     ┌───────────────────────────┐  │
                    │  │  Nginx       │────►│  Next.js 14 (Web App)     │  │
                    │  │  (proxy)     │     │  TypeScript / React       │  │
  API Client ───────►│  │             │     │  Port 3000                │  │
                    │  │             │     └───────────────────────────┘  │
                    │  │             │                                      │
                    │  │             │     ┌───────────────────────────┐  │
                    │  │             │────►│  FastAPI (REST API)       │  │
                    │  └──────────────┘    │  Python / uvicorn         │  │
                    │                      │  Port 8000                │  │
                    │                      └──────────┬────────────────┘  │
                    │                                 │                    │
                    │  ┌──────────────┐              │                    │
                    │  │  Celery      │◄─────────────┘                    │
                    │  │  Workers     │                                    │
                    │  │  Python      │                                    │
                    │  └──────┬───────┘                                    │
                    │         │                                            │
                    │  ┌──────▼───────┐    ┌──────────────────────────┐  │
                    │  │ PostgreSQL   │    │  Redis                   │  │
                    │  │ 16           │    │  (cache + task queue)    │  │
                    │  │ Port 5432    │    │  Port 6379               │  │
                    │  └─────────────┘    └──────────────────────────┘  │
                    └───────────────────────────────────────────────────────┘
```

### Level 3 – Component Diagram (API service)

```
┌─────────────────────────────────────────────────────────────────────┐
│                         FastAPI Application                          │
│                                                                      │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────────────┐  │
│  │  Auth       │  │  Jobs        │  │  Analytics               │  │
│  │  Router     │  │  Router      │  │  Router                  │  │
│  │  /auth      │  │  /jobs       │  │  /analytics              │  │
│  └──────┬──────┘  └──────┬───────┘  └────────┬─────────────────┘  │
│         │                │                   │                      │
│  ┌──────▼──────────────────▼──────────────────▼──────────────────┐ │
│  │                   Service Layer                                 │ │
│  │  AuthService  JobService  AnalyticsService  ReportService      │ │
│  └──────────────────────────┬──────────────────────────────────── ┘ │
│                             │                                        │
│  ┌──────────────────────────▼──────────────────────────────────────┐│
│  │                    Repository Layer                              ││
│  │  SQLAlchemy 2 async models + repositories                       ││
│  └──────────────────────────┬───────────────────────────────────── ┘│
│                             │                                        │
│                    PostgreSQL / Redis                                 │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Data Flow

### Ingestion Pipeline

```
France Travail API
      │
      ▼
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐
│  Connector  │────►│  Raw Storage │────►│  Normaliser     │
│  (Celery    │     │  (PostgreSQL │     │  (parse title,  │
│   beat)     │     │  raw_data    │     │   location,     │
└─────────────┘     │  JSONB)      │     │   salary)       │
                    └──────────────┘     └────────┬────────┘
                                                  │
                                         ┌────────▼────────┐
                                         │  NLP Enricher   │
                                         │  (skill extract,│
                                         │   embedding)    │
                                         └────────┬────────┘
                                                  │
                                         ┌────────▼────────┐
                                         │  job_offers     │
                                         │  + job_skills   │
                                         │  (PostgreSQL)   │
                                         └─────────────────┘
```

### Query / Analytics Flow

```
User Request
     │
     ▼
FastAPI endpoint
     │
     ├──[cache hit]──► Redis ──► Response
     │
     └──[cache miss]─► PostgreSQL
                             │
                             ▼
                       Aggregate query
                             │
                             ▼
                       Cache result (Redis TTL)
                             │
                             ▼
                          Response
```

---

## Technology Decisions

### PostgreSQL over dedicated analytics DB
**Decision**: Use PostgreSQL 16 as the primary analytics store rather than ClickHouse/BigQuery.  
**Rationale**: At the initial scale (< 10M rows), PostgreSQL with proper indexes (GIN trigram, B-tree partials) and `pg_trgm` provides sufficient query performance. This reduces operational complexity and cost. If query latency degrades past 500ms for aggregations, we can add a read replica or materialised views.

### FastAPI over Django REST Framework
**Decision**: FastAPI with async SQLAlchemy.  
**Rationale**: Native async support is critical for handling concurrent I/O-bound requests (DB + Redis + external APIs) without thread overhead. Pydantic v2 provides fast serialisation and automatic OpenAPI docs.

### Celery over custom job runner
**Decision**: Celery with Redis broker for background tasks.  
**Rationale**: Battle-tested, supports retry policies, task routing, periodic scheduling (beat), and monitoring (Flower). The France Travail API has rate limits requiring queued ingestion.

### Next.js 14 App Router
**Decision**: Next.js 14 with React Server Components.  
**Rationale**: Server-side rendering improves initial load performance for SEO-critical market dashboard pages. App Router enables fine-grained caching at the component level.

### Redis for cache + queue
**Decision**: Single Redis instance for both task queue and application cache.  
**Rationale**: Simplifies infrastructure at early stage. Production should use separate Redis instances (different eviction policies: LRU for cache, noeviction for queue).

---

## Scalability Considerations

### Horizontal scaling path

| Component | Scale Strategy |
|-----------|----------------|
| FastAPI   | Add replicas behind load balancer; stateless |
| Workers   | Increase Celery concurrency; add worker pods |
| PostgreSQL | Read replicas for analytics queries; partitioning by `created_at` on `job_offers` |
| Redis     | Redis Cluster for queue; Redis Sentinel for cache HA |
| Web       | CDN for static assets; Vercel/CloudFront edge |

### Database partitioning strategy
The `job_offers` table should be range-partitioned by `created_at` (monthly) once it exceeds ~5M rows. Partition pruning will keep analytical queries fast.

### Caching strategy
- **L1 (in-process)**: `functools.lru_cache` for static lookups (skill taxonomy, ROME codes)
- **L2 (Redis)**: Aggregated stats (salary stats, trend metrics) with 1-hour TTL
- **L3 (PostgreSQL materialised views)**: Pre-computed for dashboard landing page; refreshed every 6 hours

### Rate limiting
France Travail API allows ~2,000 calls/minute. The Celery beat schedule is capped at 1,800 calls/minute with exponential back-off on 429 responses.
