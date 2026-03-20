# Talentora AI

> **The Bloomberg for the Job Market** — Real-time European labour market intelligence for recruiters, HR teams, and job seekers.

---

## What is Talentora AI?

Talentora AI aggregates, enriches, and analyses millions of job postings across France and Europe to surface actionable market intelligence:

- **Salary benchmarks** – percentile distributions by role, location, and experience level  
- **Skills demand trends** – track which technologies are rising or falling in demand  
- **Market heat maps** – geographic demand visualisations  
- **Competitive intelligence** – monitor competitor hiring velocity  
- **Automated reports** – scheduled PDF/CSV exports for HR teams  

---

## Architecture Overview

```
┌──────────────────────────────────────────────────────────────┐
│                         Clients                              │
│          Browser (Next.js)  ·  API consumers                 │
└────────────────────┬─────────────────────────────────────────┘
                     │ HTTPS
┌────────────────────▼─────────────────────────────────────────┐
│                    Nginx (reverse proxy)                     │
└──────────┬─────────────────────────────┬─────────────────────┘
           │                             │
┌──────────▼──────────┐      ┌───────────▼──────────┐
│   FastAPI (REST)    │      │   Next.js 14 (App)   │
│   apps/api          │      │   apps/web            │
└──────────┬──────────┘      └──────────────────────┘
           │
┌──────────▼──────────────────────────────────────────────────┐
│               PostgreSQL 16     Redis 7                     │
│               (primary store)   (cache + queue)             │
└──────────────────────────────────────────────────────────────┘
           │
┌──────────▼──────────┐
│   Celery Workers    │  ← Data ingestion, NLP enrichment,
│   apps/worker       │     report generation
└──────────┬──────────┘
           │
   ┌───────▼────────────────────┐
   │   External Data Sources    │
   │  France Travail API  ·  …  │
   └────────────────────────────┘
```

See [`docs/architecture/overview.md`](docs/architecture/overview.md) for the full C4 model.

---

## Quick Start

### Prerequisites
- Docker Desktop ≥ 4.x
- Node.js ≥ 20 (for local frontend development without Docker)
- Python ≥ 3.11 (for local API development without Docker)

### 1. Clone the repository
```bash
git clone https://github.com/talentora/talentora-ai.git
cd talentora-ai
```

### 2. Configure environment variables
```bash
cp .env.example .env
# Edit .env with your API keys and secrets
```

### 3. Start the full stack
```bash
docker compose up --build
```

| Service     | URL                          |
|-------------|------------------------------|
| Web app     | http://localhost:3000        |
| API         | http://localhost:8000        |
| API docs    | http://localhost:8000/docs   |
| Flower      | http://localhost:5555        |

### 4. Seed sample data (optional)
```bash
docker compose exec api python -m infra.seed.seed_data
```

---

## Folder Structure

```
talentora-ai/
├── apps/
│   ├── api/          # FastAPI backend (Python 3.11)
│   ├── web/          # Next.js 14 frontend (TypeScript)
│   └── worker/       # Celery worker (Python 3.11)
├── packages/
│   ├── ui/           # Shared React component library
│   └── config/       # Shared ESLint / TypeScript configs
├── services/
│   └── ...           # Standalone micro-services (future)
├── infra/
│   ├── docker/       # Nginx and Docker configs
│   ├── migrations/   # SQL migrations
│   └── seed/         # Development seed data
├── docs/
│   ├── architecture/ # System design docs
│   ├── api/          # API reference
│   ├── data-sources/ # Connector docs
│   └── product/      # Roadmap, monetisation
└── tests/
    ├── unit/         # Unit tests
    ├── integration/  # Integration tests
    └── fixtures/     # Shared test data
```

---

## Tech Stack

| Layer         | Technology                     |
|---------------|--------------------------------|
| Frontend      | Next.js 14, React 18, TypeScript, Tailwind CSS |
| Backend       | FastAPI, SQLAlchemy 2, Pydantic v2 |
| Workers       | Celery, Redis                  |
| Database      | PostgreSQL 16                  |
| Cache / Queue | Redis 7                        |
| NLP           | spaCy, HuggingFace Transformers |
| Infra         | Docker, Nginx                  |
| Billing       | Stripe                         |
| Storage       | AWS S3 (eu-west-3)             |
| CI/CD         | GitHub Actions                 |

---

## Development

### Running tests
```bash
# Python unit tests
pytest tests/ -v

# Frontend lint & type check
cd apps/web && npm run lint && npx tsc --noEmit
```

### Database migrations
```bash
# Apply migrations manually
psql $DATABASE_URL -f infra/migrations/001_initial_schema.sql
```

### Adding a new data connector
See [`docs/data-sources/connectors.md`](docs/data-sources/connectors.md).

---

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feat/your-feature`
3. Commit changes: `git commit -m "feat: add your feature"`
4. Push and open a Pull Request

Please follow [Conventional Commits](https://www.conventionalcommits.org/) for commit messages.

---

## Documentation

| Document | Description |
|----------|-------------|
| [Architecture Overview](docs/architecture/overview.md) | C4 model, data flow, design decisions |
| [Data Model](docs/architecture/data-model.md) | Database schema reference |
| [API Reference](docs/api/README.md) | REST API documentation |
| [Data Connectors](docs/data-sources/connectors.md) | Adding data sources |
| [Open Source Map](docs/data-sources/open-source-map.md) | OSS projects used as inspiration |
| [Monetisation](docs/product/monetization.md) | Pricing strategy |
| [Roadmap](docs/product/roadmap.md) | Product roadmap |

---

## License

© 2024 Talentora AI SAS. All rights reserved.  
License terms TBD (Proprietary / MIT for open-sourced packages).
