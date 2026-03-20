#!/usr/bin/env python3
"""
Talentora AI – Database seed script.
Populates the database with realistic sample data for development/testing.

Usage:
    DATABASE_URL=postgresql://talentora:talentora_dev@localhost:5432/talentora \
    python infra/seed/seed_data.py
"""

from __future__ import annotations

import os
import random
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

import psycopg2
from psycopg2.extras import execute_values, RealDictCursor

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://talentora:talentora_dev@localhost:5432/talentora",
)

# ─── Sample data definitions ──────────────────────────────────────────────────

COMPANIES: list[dict[str, Any]] = [
    {
        "name": "Dataiku",
        "normalized_name": "dataiku",
        "sector": "Software",
        "industry": "Data & AI",
        "size_range": "501-1000",
        "city": "Paris",
        "region": "Île-de-France",
        "website": "https://dataiku.com",
    },
    {
        "name": "Doctolib",
        "normalized_name": "doctolib",
        "sector": "HealthTech",
        "industry": "Healthcare Technology",
        "size_range": "1001-5000",
        "city": "Paris",
        "region": "Île-de-France",
        "website": "https://doctolib.fr",
    },
    {
        "name": "Criteo",
        "normalized_name": "criteo",
        "sector": "AdTech",
        "industry": "Digital Advertising",
        "size_range": "1001-5000",
        "city": "Paris",
        "region": "Île-de-France",
        "website": "https://criteo.com",
    },
    {
        "name": "Contentsquare",
        "normalized_name": "contentsquare",
        "sector": "Analytics",
        "industry": "Digital Experience Analytics",
        "size_range": "501-1000",
        "city": "Paris",
        "region": "Île-de-France",
        "website": "https://contentsquare.com",
    },
    {
        "name": "OVHcloud",
        "normalized_name": "ovhcloud",
        "sector": "Cloud",
        "industry": "Cloud Infrastructure",
        "size_range": "5001-10000",
        "city": "Roubaix",
        "region": "Hauts-de-France",
        "website": "https://ovhcloud.com",
    },
    {
        "name": "ManoMano",
        "normalized_name": "manomano",
        "sector": "E-commerce",
        "industry": "Home Improvement",
        "size_range": "501-1000",
        "city": "Paris",
        "region": "Île-de-France",
        "website": "https://manomano.fr",
    },
    {
        "name": "Deezer",
        "normalized_name": "deezer",
        "sector": "Entertainment",
        "industry": "Music Streaming",
        "size_range": "501-1000",
        "city": "Paris",
        "region": "Île-de-France",
        "website": "https://deezer.com",
    },
    {
        "name": "Mirakl",
        "normalized_name": "mirakl",
        "sector": "Software",
        "industry": "Marketplace Technology",
        "size_range": "201-500",
        "city": "Paris",
        "region": "Île-de-France",
        "website": "https://mirakl.com",
    },
    {
        "name": "Pennylane",
        "normalized_name": "pennylane",
        "sector": "FinTech",
        "industry": "Accounting Software",
        "size_range": "51-200",
        "city": "Paris",
        "region": "Île-de-France",
        "website": "https://pennylane.com",
    },
    {
        "name": "Leboncoin",
        "normalized_name": "leboncoin",
        "sector": "Marketplace",
        "industry": "Classifieds",
        "size_range": "501-1000",
        "city": "Paris",
        "region": "Île-de-France",
        "website": "https://leboncoin.fr",
    },
]

SKILLS: list[dict[str, Any]] = [
    {"name": "Python", "slug": "python", "category": "language"},
    {"name": "TypeScript", "slug": "typescript", "category": "language"},
    {"name": "JavaScript", "slug": "javascript", "category": "language"},
    {"name": "Go", "slug": "go", "category": "language"},
    {"name": "Java", "slug": "java", "category": "language"},
    {"name": "Rust", "slug": "rust", "category": "language"},
    {"name": "SQL", "slug": "sql", "category": "language"},
    {"name": "React", "slug": "react", "category": "framework"},
    {"name": "FastAPI", "slug": "fastapi", "category": "framework"},
    {"name": "Next.js", "slug": "nextjs", "category": "framework"},
    {"name": "Django", "slug": "django", "category": "framework"},
    {"name": "Kubernetes", "slug": "kubernetes", "category": "tool"},
    {"name": "Docker", "slug": "docker", "category": "tool"},
    {"name": "Terraform", "slug": "terraform", "category": "tool"},
    {"name": "Apache Kafka", "slug": "kafka", "category": "tool"},
    {"name": "PostgreSQL", "slug": "postgresql", "category": "tool"},
    {"name": "Redis", "slug": "redis", "category": "tool"},
    {"name": "Elasticsearch", "slug": "elasticsearch", "category": "tool"},
    {"name": "Machine Learning", "slug": "machine-learning", "category": "domain"},
    {"name": "Data Engineering", "slug": "data-engineering", "category": "domain"},
]

JOB_TEMPLATES: list[dict[str, Any]] = [
    {
        "title": "Senior Data Engineer",
        "job_category": "Data Engineering",
        "experience_level": "senior",
        "experience_years_min": 4,
        "experience_years_max": 8,
        "salary_min": 65000,
        "salary_max": 85000,
        "contract_type": "CDI",
        "remote_policy": "hybrid",
    },
    {
        "title": "Lead Backend Engineer – Python",
        "job_category": "Software Engineering",
        "experience_level": "lead",
        "experience_years_min": 6,
        "experience_years_max": 12,
        "salary_min": 75000,
        "salary_max": 100000,
        "contract_type": "CDI",
        "remote_policy": "hybrid",
    },
    {
        "title": "Frontend Engineer – React / TypeScript",
        "job_category": "Software Engineering",
        "experience_level": "mid",
        "experience_years_min": 2,
        "experience_years_max": 5,
        "salary_min": 50000,
        "salary_max": 70000,
        "contract_type": "CDI",
        "remote_policy": "hybrid",
    },
    {
        "title": "Machine Learning Engineer",
        "job_category": "Data & AI",
        "experience_level": "senior",
        "experience_years_min": 3,
        "experience_years_max": 7,
        "salary_min": 70000,
        "salary_max": 95000,
        "contract_type": "CDI",
        "remote_policy": "remote",
    },
    {
        "title": "DevOps / SRE Engineer",
        "job_category": "Infrastructure",
        "experience_level": "mid",
        "experience_years_min": 3,
        "experience_years_max": 6,
        "salary_min": 55000,
        "salary_max": 75000,
        "contract_type": "CDI",
        "remote_policy": "hybrid",
    },
    {
        "title": "Data Analyst",
        "job_category": "Data Analytics",
        "experience_level": "junior",
        "experience_years_min": 0,
        "experience_years_max": 3,
        "salary_min": 38000,
        "salary_max": 52000,
        "contract_type": "CDI",
        "remote_policy": "onsite",
    },
    {
        "title": "Product Manager – Data Products",
        "job_category": "Product",
        "experience_level": "mid",
        "experience_years_min": 3,
        "experience_years_max": 7,
        "salary_min": 55000,
        "salary_max": 80000,
        "contract_type": "CDI",
        "remote_policy": "hybrid",
    },
    {
        "title": "Backend Engineer – Go",
        "job_category": "Software Engineering",
        "experience_level": "mid",
        "experience_years_min": 2,
        "experience_years_max": 5,
        "salary_min": 52000,
        "salary_max": 72000,
        "contract_type": "CDI",
        "remote_policy": "remote",
    },
    {
        "title": "Staff Engineer – Platform",
        "job_category": "Software Engineering",
        "experience_level": "lead",
        "experience_years_min": 8,
        "experience_years_max": 15,
        "salary_min": 90000,
        "salary_max": 130000,
        "contract_type": "CDI",
        "remote_policy": "hybrid",
    },
    {
        "title": "Data Scientist – NLP",
        "job_category": "Data & AI",
        "experience_level": "senior",
        "experience_years_min": 3,
        "experience_years_max": 6,
        "salary_min": 65000,
        "salary_max": 90000,
        "contract_type": "CDI",
        "remote_policy": "hybrid",
    },
]

LOCATIONS = [
    ("Paris", "Île-de-France", "75001"),
    ("Lyon", "Auvergne-Rhône-Alpes", "69001"),
    ("Bordeaux", "Nouvelle-Aquitaine", "33000"),
    ("Nantes", "Pays de la Loire", "44000"),
    ("Toulouse", "Occitanie", "31000"),
    ("Lille", "Hauts-de-France", "59000"),
    ("Rennes", "Bretagne", "35000"),
    ("Sophia Antipolis", "Provence-Alpes-Côte d'Azur", "06560"),
]

ROME_CODES = {
    "Software Engineering": "M1805",
    "Data Engineering": "M1803",
    "Data & AI": "M1801",
    "Data Analytics": "M1802",
    "Infrastructure": "M1806",
    "Product": "M1302",
}

DESCRIPTION_TEMPLATE = """
Nous recherchons un(e) {title} passionné(e) pour rejoindre notre équipe tech.

**Missions principales :**
- Concevoir et implémenter des solutions techniques robustes et scalables
- Collaborer étroitement avec les équipes produit et data
- Participer aux revues de code et améliorer la qualité du code
- Contribuer à l'architecture technique de la plateforme
- Mentorer les membres juniors de l'équipe

**Profil recherché :**
- {experience_years_min} à {experience_years_max} ans d'expérience en développement
- Maîtrise des technologies de notre stack
- Sens de la qualité et du détail
- Esprit d'équipe et capacité de communication

**Ce que nous offrons :**
- Salaire compétitif : {salary_min}–{salary_max} k€ selon profil
- Télétravail flexible ({remote_policy})
- Mutuelle haut de gamme
- Budget formation annuel
- Stock-options / BSPCE
"""


def get_connection() -> psycopg2.extensions.connection:
    """Open a database connection, stripping asyncpg prefix if present."""
    url = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")
    return psycopg2.connect(url)


def seed_workspace_and_user(cur: RealDictCursor) -> tuple[uuid.UUID, uuid.UUID]:
    """Insert a demo workspace and owner user, return (workspace_id, user_id)."""
    workspace_id = uuid.uuid4()
    cur.execute(
        """
        INSERT INTO workspaces (id, name, slug, plan, billing_status)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (slug) DO NOTHING
        RETURNING id
        """,
        (str(workspace_id), "Acme Corp", "acme-corp", "pro", "active"),
    )
    row = cur.fetchone()
    if row:
        workspace_id = row["id"]

    user_id = uuid.uuid4()
    cur.execute(
        """
        INSERT INTO users (id, workspace_id, email, full_name, role, is_active, is_verified)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (email) DO NOTHING
        RETURNING id
        """,
        (
            str(user_id),
            str(workspace_id),
            "demo@talentora.ai",
            "Demo User",
            "owner",
            True,
            True,
        ),
    )
    row = cur.fetchone()
    if row:
        user_id = row["id"]

    return workspace_id, user_id


def seed_companies(cur: RealDictCursor) -> list[uuid.UUID]:
    company_ids: list[uuid.UUID] = []
    for c in COMPANIES:
        cid = uuid.uuid4()
        cur.execute(
            """
            INSERT INTO companies (id, name, normalized_name, sector, industry,
                                   size_range, city, region, website)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT DO NOTHING
            RETURNING id
            """,
            (
                str(cid),
                c["name"],
                c["normalized_name"],
                c["sector"],
                c["industry"],
                c["size_range"],
                c["city"],
                c["region"],
                c["website"],
            ),
        )
        row = cur.fetchone()
        company_ids.append(row["id"] if row else cid)
    return company_ids


def seed_skills(cur: RealDictCursor) -> list[uuid.UUID]:
    skill_ids: list[uuid.UUID] = []
    for s in SKILLS:
        sid = uuid.uuid4()
        cur.execute(
            """
            INSERT INTO skills (id, name, slug, category)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (slug) DO NOTHING
            RETURNING id
            """,
            (str(sid), s["name"], s["slug"], s["category"]),
        )
        row = cur.fetchone()
        skill_ids.append(row["id"] if row else sid)
    return skill_ids


def seed_job_offers(
    cur: RealDictCursor,
    company_ids: list[uuid.UUID],
    skill_ids: list[uuid.UUID],
) -> None:
    now = datetime.now(timezone.utc)
    job_rows: list[tuple] = []

    templates = JOB_TEMPLATES * 5  # 50 offers = 10 templates × 5

    for i, tpl in enumerate(templates):
        city, region, postal = random.choice(LOCATIONS)
        company_id = random.choice(company_ids)
        published_at = now - timedelta(days=random.randint(0, 60))
        source_id = f"SEED_{i:05d}"

        description = DESCRIPTION_TEMPLATE.format(
            title=tpl["title"],
            experience_years_min=tpl["experience_years_min"],
            experience_years_max=tpl["experience_years_max"],
            salary_min=tpl["salary_min"] // 1000,
            salary_max=tpl["salary_max"] // 1000,
            remote_policy=tpl["remote_policy"],
        )

        job_rows.append(
            (
                str(uuid.uuid4()),
                "seed",
                source_id,
                str(company_id),
                tpl["title"],
                tpl["title"].lower(),
                description.strip(),
                tpl["job_category"],
                ROME_CODES.get(tpl["job_category"], "M1805"),
                city,
                region,
                postal,
                tpl["contract_type"],
                tpl["experience_level"],
                tpl["experience_years_min"],
                tpl["experience_years_max"],
                tpl["salary_min"],
                tpl["salary_max"],
                "EUR",
                "annual",
                f"{tpl['salary_min']//1000}–{tpl['salary_max']//1000} k€",
                "active",
                published_at,
                tpl["remote_policy"],
            )
        )

    execute_values(
        cur,
        """
        INSERT INTO job_offers (
            id, source, source_id, company_id, title, normalized_title,
            description, job_category, rome_code, city, region, postal_code,
            contract_type, experience_level, experience_years_min, experience_years_max,
            salary_min, salary_max, salary_currency, salary_period, salary_raw,
            status, published_at, remote_policy
        ) VALUES %s
        ON CONFLICT (source, source_id) DO NOTHING
        """,
        job_rows,
    )

    # Attach random skills to each job offer
    cur.execute("SELECT id FROM job_offers WHERE source = 'seed'")
    job_ids = [row["id"] for row in cur.fetchall()]

    skill_rows: list[tuple] = []
    for job_id in job_ids:
        chosen = random.sample(skill_ids, k=random.randint(3, 7))
        for idx, skill_id in enumerate(chosen):
            skill_rows.append(
                (str(job_id), str(skill_id), idx < 3, round(random.uniform(0.7, 0.99), 4))
            )

    execute_values(
        cur,
        """
        INSERT INTO job_skills (job_offer_id, skill_id, is_required, confidence)
        VALUES %s
        ON CONFLICT DO NOTHING
        """,
        skill_rows,
    )


def main() -> None:
    print("🌱  Connecting to database…")
    conn = get_connection()
    conn.autocommit = False

    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            print("  → Seeding workspace and user…")
            seed_workspace_and_user(cur)

            print("  → Seeding companies…")
            company_ids = seed_companies(cur)
            print(f"     {len(company_ids)} companies inserted.")

            print("  → Seeding skills…")
            skill_ids = seed_skills(cur)
            print(f"     {len(skill_ids)} skills inserted.")

            print("  → Seeding job offers and skills…")
            seed_job_offers(cur, company_ids, skill_ids)
            print("     50 job offers inserted.")

        conn.commit()
        print("✅  Seed completed successfully.")

    except Exception:
        conn.rollback()
        print("❌  Seed failed – rolled back.")
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    main()
