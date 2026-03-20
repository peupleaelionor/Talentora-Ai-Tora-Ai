from app.routers import health
from app.routers import auth
from app.routers import jobs
from app.routers import companies
from app.routers import skills
from app.routers import trends
from app.routers import reports
from app.routers import search
from app.routers import billing
from app.routers import admin
from app.routers import ingestion

__all__ = [
    "health",
    "auth",
    "jobs",
    "companies",
    "skills",
    "trends",
    "reports",
    "search",
    "billing",
    "admin",
    "ingestion",
]
