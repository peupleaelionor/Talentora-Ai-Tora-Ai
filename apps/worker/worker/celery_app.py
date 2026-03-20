"""
Celery application configuration for the Talentora background worker.

Configures Redis broker/backend, task routing, rate limits, and
scheduled periodic tasks (daily ingestion, weekly trend computation).
"""

from __future__ import annotations

import os
from datetime import timedelta

from celery import Celery
from celery.schedules import crontab
from kombu import Exchange, Queue

# ---------------------------------------------------------------------------
# Broker / backend
# ---------------------------------------------------------------------------

REDIS_URL: str = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
REDIS_BACKEND: str = os.environ.get("REDIS_BACKEND_URL", REDIS_URL)

app = Celery("talentora_worker")

app.conf.update(
    # ---- transport ----
    broker_url=REDIS_URL,
    result_backend=REDIS_BACKEND,
    broker_connection_retry_on_startup=True,
    # ---- serialisation ----
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    # ---- time-zones ----
    timezone="Europe/Paris",
    enable_utc=True,
    # ---- result retention ----
    result_expires=timedelta(days=7),
    # ---- task execution ----
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    worker_prefetch_multiplier=1,
    task_track_started=True,
    # ---- visibility timeout (must be > longest task runtime) ----
    broker_transport_options={"visibility_timeout": 3600},
)

# ---------------------------------------------------------------------------
# Named queues and routing
# ---------------------------------------------------------------------------

default_exchange = Exchange("default", type="direct")
ingestion_exchange = Exchange("ingestion", type="direct")
analysis_exchange = Exchange("analysis", type="direct")
reporting_exchange = Exchange("reporting", type="direct")

app.conf.task_queues = (
    Queue("default", default_exchange, routing_key="default"),
    Queue("ingestion", ingestion_exchange, routing_key="ingestion"),
    Queue("analysis", analysis_exchange, routing_key="analysis"),
    Queue("reporting", reporting_exchange, routing_key="reporting"),
)

app.conf.task_default_queue = "default"
app.conf.task_default_exchange = "default"
app.conf.task_default_routing_key = "default"

app.conf.task_routes = {
    # ingestion tasks
    "worker.tasks.ingestion.*": {"queue": "ingestion"},
    # analysis tasks
    "worker.tasks.analysis.*": {"queue": "analysis"},
    # reporting tasks
    "worker.tasks.reporting.*": {"queue": "reporting"},
    # normalization alongside ingestion
    "worker.tasks.normalization.*": {"queue": "ingestion"},
}

# ---------------------------------------------------------------------------
# Rate limits per task type
# ---------------------------------------------------------------------------

app.conf.task_annotations = {
    "worker.tasks.ingestion.fetch_jobs_from_source": {"rate_limit": "10/m"},
    "worker.tasks.ingestion.process_raw_job": {"rate_limit": "60/m"},
    "worker.tasks.analysis.generate_embeddings": {"rate_limit": "30/m"},
}

# ---------------------------------------------------------------------------
# Periodic / scheduled tasks (Celery Beat)
# ---------------------------------------------------------------------------

app.conf.beat_schedule = {
    # Daily full ingestion run at 02:00 Europe/Paris
    "daily-ingestion": {
        "task": "worker.tasks.ingestion.run_all_sources",
        "schedule": crontab(hour=2, minute=0),
        "options": {"queue": "ingestion"},
    },
    # Weekly trend computation every Sunday at 03:00
    "weekly-trend-computation": {
        "task": "worker.tasks.analysis.compute_trends",
        "schedule": crontab(hour=3, minute=0, day_of_week=0),
        "kwargs": {"timeframe": "7d"},
        "options": {"queue": "analysis"},
    },
    # Daily salary stats refresh at 04:00
    "daily-salary-stats": {
        "task": "worker.tasks.reporting.generate_salary_report",
        "schedule": crontab(hour=4, minute=0),
        "options": {"queue": "reporting"},
    },
    # Incremental ingestion every 6 hours during business hours
    "incremental-ingestion": {
        "task": "worker.tasks.ingestion.run_all_sources",
        "schedule": crontab(hour="8,14,20", minute=30),
        "kwargs": {"incremental": True},
        "options": {"queue": "ingestion"},
    },
}

# ---------------------------------------------------------------------------
# Auto-discover tasks from the worker package
# ---------------------------------------------------------------------------

app.autodiscover_tasks(["worker.tasks"])
