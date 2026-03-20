# Open Source Map

Research document: OSS projects that inform Talentora AI's architecture.

---

## 1. SeleniumHQ/selenium
**What it does**: Browser automation via WebDriver protocol.  
**Talentora reuse**: Fallback scraping for job boards without public APIs.  
**Reimplement**: Wrap in Celery tasks with rotating proxies and headless Chrome.  
**License**: Apache 2.0 ✅

## 2. microsoft/playwright
**What it does**: Modern async browser automation with better reliability than Selenium.  
**Talentora reuse**: Preferred over Selenium for new scraper targets; native async fits our Celery workers.  
**Reimplement**: Create thin `PlaywrightConnector` base class with stealth patches.  
**License**: Apache 2.0 ✅

## 3. Bunsly/jobspy
**What it does**: Python library scraping LinkedIn, Indeed, Glassdoor, Google Jobs.  
**Talentora reuse**: Study its normalisation patterns; do NOT import directly (TOS risk).  
**Reimplement**: Build our own connectors inspired by its field mapping (`salary_min`, `salary_max`, `job_type`).  
**License**: MIT ✅ (but scraped sites' TOS may restrict use)

## 4. explosion/spaCy
**What it does**: Industrial-strength NLP — tokenisation, NER, dependency parsing.  
**Talentora reuse**: Skill entity extraction from job descriptions using custom NER model trained on labelled job postings.  
**Reimplement**: Fine-tune `fr_core_news_lg` with a custom `SKILL` entity type.  
**License**: MIT ✅

## 5. huggingface/transformers
**What it does**: State-of-the-art text classification, embeddings, generation.  
**Talentora reuse**: `sentence-transformers/paraphrase-multilingual-mpnet-base-v2` for job offer similarity; zero-shot classification for role taxonomy.  
**Reimplement**: Wrap inference in a Celery task; cache embeddings in pgvector column.  
**License**: Apache 2.0 ✅

## 6. elastic/elasticsearch
**What it does**: Distributed full-text search and analytics engine.  
**Talentora reuse**: Study its aggregation API design (histogram, terms, percentiles) for our PostgreSQL query layer.  
**Reimplement**: PostgreSQL + `pg_trgm` + materialised views replicate 80% of use cases at our scale. Add ES if search latency > 200ms.  
**License**: SSPL (not OSS for SaaS use) ⚠️ — use OpenSearch Apache 2.0 alternative.

## 7. supabase/supabase
**What it does**: Open-source Firebase alternative (PostgreSQL + Auth + Storage + Realtime).  
**Talentora reuse**: Architecture inspiration — Auth module design, Row Level Security patterns for workspace isolation.  
**Reimplement**: Build our own auth with FastAPI + JWT; apply RLS policies on PostgreSQL for tenant isolation.  
**License**: Apache 2.0 ✅

## 8. airbytehq/airbyte
**What it does**: Open-source data integration platform with 300+ connectors.  
**Talentora reuse**: Connector specification pattern (Source → Catalog → Stream → Record); incremental sync with state cursors.  
**Reimplement**: Adopt the `cursor_field` + `state` pattern in our `BaseConnector` for resumable ingestion.  
**License**: MIT / ELv2 ✅ for self-hosted

## 9. apache/airflow
**What it does**: Workflow orchestration with DAG-based scheduling.  
**Talentora reuse**: DAG design patterns for multi-step pipelines; sensor tasks for API availability checks.  
**Reimplement**: Celery beat for scheduling; Celery chains/groups for DAG-like task pipelines. Migrate to Airflow if pipeline complexity grows beyond 20 DAGs.  
**License**: Apache 2.0 ✅

## 10. scrapfly/scrapfly-scrapy
**What it does**: Industrial web scraping with anti-bot bypass, proxy rotation.  
**Talentora reuse**: Architecture pattern for scraper middleware stack (retry, proxy rotation, browser fingerprinting).  
**Reimplement**: Build `ScraperMiddleware` inspired by its session management; use Playwright stealth plugin.  
**License**: Apache 2.0 ✅
