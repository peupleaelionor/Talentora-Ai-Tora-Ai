# Data Model

## Entity Relationship Overview

```
workspaces ──< users
workspaces ──< reports
workspaces ──< search_queries
users ──< reports
users ──< audit_logs
companies ──< job_offers
job_offers ──< job_skills >── skills
skills ──< salary_stats
skills ──< trend_metrics
```

## Entities

### workspaces
| Column | Type | Description |
|--------|------|-------------|
| id | UUID PK | |
| name | VARCHAR(255) | Display name |
| slug | VARCHAR(100) UNIQUE | URL-safe identifier |
| plan | ENUM | free/starter/pro/team/enterprise |
| billing_status | ENUM | active/past_due/canceled/trialing |
| stripe_customer_id | VARCHAR | Stripe customer reference |
| settings | JSONB | Feature flags and preferences |
| created_at | TIMESTAMPTZ | |

### users
| Column | Type | Description |
|--------|------|-------------|
| id | UUID PK | |
| workspace_id | UUID FK → workspaces | |
| email | VARCHAR(320) UNIQUE | |
| hashed_password | VARCHAR | bcrypt; NULL for OAuth |
| role | ENUM | owner/admin/member/viewer |
| is_active | BOOLEAN | |
| is_verified | BOOLEAN | Email verified |

### companies
| Column | Type | Description |
|--------|------|-------------|
| id | UUID PK | |
| name | VARCHAR(500) | Original name |
| normalized_name | VARCHAR(500) | Dedup key |
| siren | CHAR(9) | French company ID |
| sector / industry | VARCHAR | Classification |
| size_range | VARCHAR | e.g. "51-200" |

### job_offers
| Column | Type | Description |
|--------|------|-------------|
| id | UUID PK | |
| source | VARCHAR(100) | Connector ID |
| source_id | VARCHAR(500) | Origin system ID |
| company_id | UUID FK | |
| title / normalized_title | VARCHAR(500) | |
| description | TEXT | Plain text |
| rome_code | VARCHAR(10) | French ROME v4 |
| city/region/country | VARCHAR | Location |
| remote_policy | VARCHAR | onsite/hybrid/remote |
| contract_type | ENUM | CDI/CDD/Stage/… |
| experience_level | ENUM | junior/mid/senior/lead |
| salary_min/max | DECIMAL(12,2) | Annual EUR |
| salary_raw | VARCHAR(500) | Original string |
| status | ENUM | active/expired/filled |
| raw_data | JSONB | Full source payload |

### skills
| Column | Type | Description |
|--------|------|-------------|
| id | UUID PK | |
| name | VARCHAR(255) UNIQUE | Canonical name |
| slug | VARCHAR(255) UNIQUE | URL key |
| category | VARCHAR | language/framework/tool/soft |
| aliases | TEXT[] | Alternative spellings |

### job_skills (junction)
| Column | Type |
|--------|------|
| job_offer_id | UUID FK |
| skill_id | UUID FK |
| is_required | BOOLEAN |
| confidence | DECIMAL(5,4) |

### salary_stats
Pre-aggregated salary distributions per segment. Updated nightly by Celery beat.

### trend_metrics
Daily snapshots of job count, growth rates per dimension (skill/role/region/sector).

### reports
Async-generated market analysis reports stored as JSONB or S3 URL.

### audit_logs
Immutable GDPR-compliant event log. Never updated or deleted.
