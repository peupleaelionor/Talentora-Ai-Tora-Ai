from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class JobOfferCreate(BaseModel):
    source: str = Field(..., max_length=100)
    source_job_id: Optional[str] = Field(None, max_length=255)
    source_url: Optional[str] = None
    application_url: Optional[str] = None

    title: str = Field(..., max_length=500)
    company_name: Optional[str] = Field(None, max_length=500)
    company_id: Optional[uuid.UUID] = None

    city: Optional[str] = Field(None, max_length=200)
    region: Optional[str] = Field(None, max_length=200)
    country: Optional[str] = Field(None, max_length=100)

    remote_type: str = Field(default="unknown")
    contract_type: Optional[str] = Field(None, max_length=100)

    salary_min: Optional[float] = Field(None, ge=0)
    salary_max: Optional[float] = Field(None, ge=0)
    salary_currency: Optional[str] = Field(None, max_length=10)

    experience_level: Optional[str] = Field(None, max_length=100)
    seniority: Optional[str] = Field(None, max_length=100)

    description_raw: Optional[str] = None
    description_clean: Optional[str] = None

    skills_raw: Optional[List[str]] = None
    skills_normalized: Optional[List[str]] = None
    technologies: Optional[List[str]] = None
    keywords: Optional[List[str]] = None
    responsibilities: Optional[List[str]] = None
    benefits: Optional[List[str]] = None

    language: Optional[str] = Field(None, max_length=10)
    posted_at: Optional[datetime] = None
    scraped_at: Optional[datetime] = None


class JobOfferUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=500)
    company_name: Optional[str] = Field(None, max_length=500)
    company_id: Optional[uuid.UUID] = None

    city: Optional[str] = None
    region: Optional[str] = None
    country: Optional[str] = None
    remote_type: Optional[str] = None
    contract_type: Optional[str] = None

    salary_min: Optional[float] = Field(None, ge=0)
    salary_max: Optional[float] = Field(None, ge=0)
    salary_currency: Optional[str] = None

    experience_level: Optional[str] = None
    seniority: Optional[str] = None

    description_raw: Optional[str] = None
    description_clean: Optional[str] = None

    skills_raw: Optional[List[str]] = None
    skills_normalized: Optional[List[str]] = None
    technologies: Optional[List[str]] = None
    keywords: Optional[List[str]] = None
    responsibilities: Optional[List[str]] = None
    benefits: Optional[List[str]] = None

    language: Optional[str] = None
    status: Optional[str] = None
    posted_at: Optional[datetime] = None


class JobOfferResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    source: str
    source_job_id: Optional[str]
    source_url: Optional[str]
    application_url: Optional[str]

    title: str
    company_name: Optional[str]
    company_id: Optional[uuid.UUID]

    city: Optional[str]
    region: Optional[str]
    country: Optional[str]
    remote_type: str
    contract_type: Optional[str]

    salary_min: Optional[float]
    salary_max: Optional[float]
    salary_currency: Optional[str]

    experience_level: Optional[str]
    seniority: Optional[str]

    description_clean: Optional[str]

    skills_normalized: Optional[List[str]]
    technologies: Optional[List[str]]
    keywords: Optional[List[str]]
    benefits: Optional[List[str]]

    language: Optional[str]
    status: str
    dedupe_hash: Optional[str]

    posted_at: Optional[datetime]
    scraped_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime


class JobOfferListResponse(BaseModel):
    items: List[JobOfferResponse]
    total: int
    page: int
    page_size: int
    pages: int
