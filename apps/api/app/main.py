from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncGenerator

import structlog
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

from app.config import settings
from app.database import engine, Base
from app.middleware.auth import AuthMiddleware
from app.middleware.rate_limit import RateLimitMiddleware
from app.routers import (
    health,
    auth,
    jobs,
    companies,
    skills,
    trends,
    reports,
    search,
    billing,
    admin,
    ingestion,
)

structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(settings.log_level_int),
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
)

logger = structlog.get_logger(__name__)

REQUEST_COUNT = Counter(
    "talentora_http_requests_total",
    "Total HTTP request count",
    ["method", "endpoint", "status_code"],
)
REQUEST_LATENCY = Histogram(
    "talentora_http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "endpoint"],
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info("Starting Talentora AI API", version=settings.API_VERSION, env=settings.ENVIRONMENT)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database connection established")
    yield
    await engine.dispose()
    logger.info("Database connection closed")


app = FastAPI(
    title="Talentora AI API",
    version="0.1.0",
    description=(
        "European job market intelligence SaaS — real-time job posting aggregation, "
        "skill extraction, salary benchmarking, and trend analytics."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url=f"/api/{settings.API_VERSION}/openapi.json",
    lifespan=lifespan,
)

# ---------------------------------------------------------------------------
# Middleware (outermost → innermost — order matters)
# ---------------------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(RateLimitMiddleware)
app.add_middleware(AuthMiddleware)


# ---------------------------------------------------------------------------
# Prometheus instrumentation
# ---------------------------------------------------------------------------

@app.middleware("http")
async def _prometheus_middleware(request: Request, call_next: any) -> Response:
    endpoint = request.url.path
    method = request.method
    with REQUEST_LATENCY.labels(method=method, endpoint=endpoint).time():
        response: Response = await call_next(request)
    REQUEST_COUNT.labels(method=method, endpoint=endpoint, status_code=response.status_code).inc()
    return response


@app.get("/metrics", include_in_schema=False)
async def metrics() -> Response:
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------

API_PREFIX = f"/api/{settings.API_VERSION}"

app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(auth.router, prefix=f"{API_PREFIX}/auth", tags=["auth"])
app.include_router(jobs.router, prefix=f"{API_PREFIX}/jobs", tags=["jobs"])
app.include_router(companies.router, prefix=f"{API_PREFIX}/companies", tags=["companies"])
app.include_router(skills.router, prefix=f"{API_PREFIX}/skills", tags=["skills"])
app.include_router(trends.router, prefix=f"{API_PREFIX}/trends", tags=["trends"])
app.include_router(reports.router, prefix=f"{API_PREFIX}/reports", tags=["reports"])
app.include_router(search.router, prefix=f"{API_PREFIX}/search", tags=["search"])
app.include_router(billing.router, prefix=f"{API_PREFIX}/billing", tags=["billing"])
app.include_router(admin.router, prefix=f"{API_PREFIX}/admin", tags=["admin"])
app.include_router(ingestion.router, prefix=f"{API_PREFIX}/ingestion", tags=["ingestion"])
