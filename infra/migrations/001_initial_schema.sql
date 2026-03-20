-- =============================================================================
-- Migration 001 – Initial Schema
-- Talentora AI – European Job Market Intelligence Platform
-- =============================================================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";   -- trigram indexes for full-text search
CREATE EXTENSION IF NOT EXISTS "btree_gin";  -- GIN index support for composite searches

-- =============================================================================
-- ENUMS
-- =============================================================================

CREATE TYPE plan_type AS ENUM ('free', 'starter', 'pro', 'team', 'enterprise');
CREATE TYPE billing_status_type AS ENUM ('active', 'past_due', 'canceled', 'trialing', 'incomplete');
CREATE TYPE user_role AS ENUM ('owner', 'admin', 'member', 'viewer');
CREATE TYPE contract_type AS ENUM ('CDI', 'CDD', 'Stage', 'Alternance', 'Freelance', 'Interim', 'Other');
CREATE TYPE experience_level AS ENUM ('junior', 'mid', 'senior', 'lead', 'executive', 'unknown');
CREATE TYPE job_status AS ENUM ('active', 'expired', 'filled', 'draft');
CREATE TYPE report_type AS ENUM ('salary_benchmark', 'skills_gap', 'market_trend', 'company_analysis', 'custom');
CREATE TYPE report_status AS ENUM ('pending', 'processing', 'completed', 'failed');

-- =============================================================================
-- TABLE: workspaces
-- Tenant/organisation container. All data is scoped to a workspace.
-- =============================================================================

CREATE TABLE workspaces (
    id              UUID        PRIMARY KEY DEFAULT uuid_generate_v4(),
    name            VARCHAR(255) NOT NULL,
    slug            VARCHAR(100) NOT NULL UNIQUE,
    plan            plan_type   NOT NULL DEFAULT 'free',
    billing_status  billing_status_type NOT NULL DEFAULT 'active',
    stripe_customer_id  VARCHAR(255),
    stripe_subscription_id VARCHAR(255),
    settings        JSONB       NOT NULL DEFAULT '{}',
    -- Quotas
    monthly_api_calls   INTEGER NOT NULL DEFAULT 0,
    monthly_api_limit   INTEGER NOT NULL DEFAULT 100,
    -- Timestamps
    trial_ends_at   TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE workspaces IS 'Tenant organisations – top-level billing and data boundary.';
COMMENT ON COLUMN workspaces.slug IS 'URL-safe unique identifier used in routes.';
COMMENT ON COLUMN workspaces.settings IS 'Flexible JSONB bag for per-workspace feature flags and preferences.';

CREATE INDEX idx_workspaces_slug ON workspaces (slug);
CREATE INDEX idx_workspaces_stripe_customer ON workspaces (stripe_customer_id) WHERE stripe_customer_id IS NOT NULL;

-- =============================================================================
-- TABLE: users
-- Platform users, always associated with exactly one workspace.
-- =============================================================================

CREATE TABLE users (
    id              UUID        PRIMARY KEY DEFAULT uuid_generate_v4(),
    workspace_id    UUID        NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    email           VARCHAR(320) NOT NULL UNIQUE,
    full_name       VARCHAR(255),
    hashed_password VARCHAR(255),          -- NULL for OAuth-only accounts
    role            user_role   NOT NULL DEFAULT 'member',
    avatar_url      TEXT,
    is_active       BOOLEAN     NOT NULL DEFAULT TRUE,
    is_verified     BOOLEAN     NOT NULL DEFAULT FALSE,
    last_login_at   TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE users IS 'Platform users with workspace membership and role-based access.';
COMMENT ON COLUMN users.hashed_password IS 'bcrypt hash. NULL when user authenticates only via OAuth provider.';

CREATE INDEX idx_users_workspace ON users (workspace_id);
CREATE INDEX idx_users_email ON users (email);

-- =============================================================================
-- TABLE: companies
-- Employer companies extracted from job offers.
-- =============================================================================

CREATE TABLE companies (
    id              UUID        PRIMARY KEY DEFAULT uuid_generate_v4(),
    name            VARCHAR(500) NOT NULL,
    normalized_name VARCHAR(500),           -- lowercased, de-duplicated form
    siren           CHAR(9),               -- French company registration number
    siret           CHAR(14),
    sector          VARCHAR(255),
    industry        VARCHAR(255),
    size_range      VARCHAR(50),           -- e.g. "51-200", "1001-5000"
    city            VARCHAR(255),
    region          VARCHAR(255),
    country         VARCHAR(100) NOT NULL DEFAULT 'France',
    website         TEXT,
    logo_url        TEXT,
    linkedin_url    TEXT,
    description     TEXT,
    metadata        JSONB        NOT NULL DEFAULT '{}',
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE companies IS 'Employer entities normalised from job offer sources.';
COMMENT ON COLUMN companies.siren IS '9-digit French company identifier (SIRENE registry).';
COMMENT ON COLUMN companies.normalized_name IS 'Lowercase, accent-stripped name used for deduplication matching.';

CREATE INDEX idx_companies_normalized_name ON companies (normalized_name);
CREATE INDEX idx_companies_siren ON companies (siren) WHERE siren IS NOT NULL;
CREATE INDEX idx_companies_sector ON companies (sector);
CREATE INDEX idx_companies_name_trgm ON companies USING gin (name gin_trgm_ops);

-- =============================================================================
-- TABLE: job_offers
-- Core entity – a single job posting ingested from any source.
-- =============================================================================

CREATE TABLE job_offers (
    id                  UUID        PRIMARY KEY DEFAULT uuid_generate_v4(),
    -- Source tracking
    source              VARCHAR(100) NOT NULL,                -- 'france_travail', 'linkedin', 'indeed', …
    source_id           VARCHAR(500),                         -- ID in the origin system
    source_url          TEXT,
    -- Company
    company_id          UUID        REFERENCES companies(id) ON DELETE SET NULL,
    company_name        VARCHAR(500),                         -- denormalised copy for resilience
    -- Job details
    title               VARCHAR(500) NOT NULL,
    normalized_title    VARCHAR(500),                         -- cleaned, canonical title
    description         TEXT,
    description_html    TEXT,
    job_category        VARCHAR(255),
    rome_code           VARCHAR(10),                          -- French ROME occupation code
    -- Location
    city                VARCHAR(255),
    region              VARCHAR(255),
    department          VARCHAR(100),
    postal_code         VARCHAR(20),
    country             VARCHAR(100) NOT NULL DEFAULT 'France',
    remote_policy       VARCHAR(50),                         -- 'onsite', 'hybrid', 'remote', 'unknown'
    latitude            DECIMAL(9,6),
    longitude           DECIMAL(9,6),
    -- Contract & experience
    contract_type       contract_type NOT NULL DEFAULT 'Other',
    experience_level    experience_level NOT NULL DEFAULT 'unknown',
    experience_years_min INTEGER,
    experience_years_max INTEGER,
    -- Salary
    salary_min          DECIMAL(12,2),
    salary_max          DECIMAL(12,2),
    salary_currency     CHAR(3) DEFAULT 'EUR',
    salary_period       VARCHAR(20),                         -- 'annual', 'monthly', 'daily', 'hourly'
    salary_raw          VARCHAR(500),                        -- original salary string before parsing
    -- Status & lifecycle
    status              job_status  NOT NULL DEFAULT 'active',
    published_at        TIMESTAMPTZ,
    expires_at          TIMESTAMPTZ,
    -- NLP enrichment
    embedding           vector(1536),                        -- pgvector embedding (if extension installed)
    language            CHAR(5) DEFAULT 'fr',
    -- Audit
    raw_data            JSONB        NOT NULL DEFAULT '{}',  -- full original payload
    created_at          TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    -- Uniqueness per source
    UNIQUE (source, source_id)
);

COMMENT ON TABLE job_offers IS 'Canonical job postings ingested and normalised from all data sources.';
COMMENT ON COLUMN job_offers.source IS 'Originating connector identifier.';
COMMENT ON COLUMN job_offers.rome_code IS 'ROME v4 occupation code from the French DARES classification.';
COMMENT ON COLUMN job_offers.remote_policy IS 'Standardised remote-work policy parsed from the posting.';
COMMENT ON COLUMN job_offers.raw_data IS 'Immutable copy of the source API payload for reprocessing.';

-- Performance indexes
CREATE INDEX idx_job_offers_source ON job_offers (source, source_id);
CREATE INDEX idx_job_offers_company ON job_offers (company_id);
CREATE INDEX idx_job_offers_contract ON job_offers (contract_type);
CREATE INDEX idx_job_offers_experience ON job_offers (experience_level);
CREATE INDEX idx_job_offers_status ON job_offers (status);
CREATE INDEX idx_job_offers_published ON job_offers (published_at DESC);
CREATE INDEX idx_job_offers_city ON job_offers (city);
CREATE INDEX idx_job_offers_region ON job_offers (region);
CREATE INDEX idx_job_offers_rome ON job_offers (rome_code);
CREATE INDEX idx_job_offers_salary ON job_offers (salary_min, salary_max);
CREATE INDEX idx_job_offers_title_trgm ON job_offers USING gin (title gin_trgm_ops);
CREATE INDEX idx_job_offers_description_trgm ON job_offers USING gin (description gin_trgm_ops);
CREATE INDEX idx_job_offers_created ON job_offers (created_at DESC);

-- =============================================================================
-- TABLE: skills
-- Canonical skill taxonomy (technologies, frameworks, soft skills, certifications)
-- =============================================================================

CREATE TABLE skills (
    id              UUID        PRIMARY KEY DEFAULT uuid_generate_v4(),
    name            VARCHAR(255) NOT NULL UNIQUE,
    slug            VARCHAR(255) NOT NULL UNIQUE,
    category        VARCHAR(100),          -- 'language', 'framework', 'tool', 'soft', 'cert', …
    aliases         TEXT[]      NOT NULL DEFAULT '{}',
    description     TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE skills IS 'Normalised skill taxonomy used across the platform.';
COMMENT ON COLUMN skills.aliases IS 'Alternative spellings/names, e.g. ["JS", "JavaScript"] for "javascript".';

CREATE INDEX idx_skills_category ON skills (category);
CREATE INDEX idx_skills_slug ON skills (slug);

-- =============================================================================
-- TABLE: job_skills
-- Many-to-many junction: which skills appear in which job offer.
-- =============================================================================

CREATE TABLE job_skills (
    job_offer_id    UUID        NOT NULL REFERENCES job_offers(id) ON DELETE CASCADE,
    skill_id        UUID        NOT NULL REFERENCES skills(id) ON DELETE CASCADE,
    is_required     BOOLEAN     NOT NULL DEFAULT TRUE,
    confidence      DECIMAL(5,4),          -- 0.0–1.0 NLP confidence score
    PRIMARY KEY (job_offer_id, skill_id)
);

COMMENT ON TABLE job_skills IS 'Skills extracted from job offer descriptions.';
COMMENT ON COLUMN job_skills.confidence IS 'NLP model confidence in skill detection (0–1).';
COMMENT ON COLUMN job_skills.is_required IS 'TRUE = must-have, FALSE = nice-to-have.';

CREATE INDEX idx_job_skills_skill ON job_skills (skill_id);
CREATE INDEX idx_job_skills_required ON job_skills (skill_id) WHERE is_required = TRUE;

-- =============================================================================
-- TABLE: salary_stats
-- Aggregated salary statistics per segment (for market intelligence dashboards)
-- =============================================================================

CREATE TABLE salary_stats (
    id              UUID        PRIMARY KEY DEFAULT uuid_generate_v4(),
    -- Dimensions
    period_year     SMALLINT    NOT NULL,
    period_month    SMALLINT,                  -- NULL = annual aggregate
    title           VARCHAR(500),
    experience_level experience_level,
    contract_type   contract_type,
    region          VARCHAR(255),
    skill_id        UUID        REFERENCES skills(id) ON DELETE SET NULL,
    -- Metrics
    sample_size     INTEGER     NOT NULL,
    salary_min      DECIMAL(12,2),
    salary_p10      DECIMAL(12,2),
    salary_p25      DECIMAL(12,2),
    salary_median   DECIMAL(12,2),
    salary_p75      DECIMAL(12,2),
    salary_p90      DECIMAL(12,2),
    salary_max      DECIMAL(12,2),
    salary_mean     DECIMAL(12,2),
    salary_stddev   DECIMAL(12,2),
    currency        CHAR(3)     NOT NULL DEFAULT 'EUR',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE salary_stats IS 'Pre-aggregated salary statistics for fast dashboard queries.';

CREATE INDEX idx_salary_stats_period ON salary_stats (period_year, period_month);
CREATE INDEX idx_salary_stats_title ON salary_stats (title);
CREATE INDEX idx_salary_stats_region ON salary_stats (region);
CREATE INDEX idx_salary_stats_skill ON salary_stats (skill_id);

-- =============================================================================
-- TABLE: trend_metrics
-- Time-series demand/supply metrics per skill or category
-- =============================================================================

CREATE TABLE trend_metrics (
    id              UUID        PRIMARY KEY DEFAULT uuid_generate_v4(),
    metric_date     DATE        NOT NULL,
    dimension_type  VARCHAR(50) NOT NULL,   -- 'skill', 'role', 'region', 'sector'
    dimension_value VARCHAR(500) NOT NULL,
    -- Counts
    job_count       INTEGER     NOT NULL DEFAULT 0,
    new_postings    INTEGER     NOT NULL DEFAULT 0,
    avg_days_open   DECIMAL(8,2),
    -- Salary snapshot
    median_salary   DECIMAL(12,2),
    -- Growth metrics
    wow_growth      DECIMAL(8,4),           -- week-over-week %
    mom_growth      DECIMAL(8,4),           -- month-over-month %
    yoy_growth      DECIMAL(8,4),           -- year-over-year %
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (metric_date, dimension_type, dimension_value)
);

COMMENT ON TABLE trend_metrics IS 'Daily snapshots of demand metrics per dimension for trend charts.';

CREATE INDEX idx_trend_metrics_date ON trend_metrics (metric_date DESC);
CREATE INDEX idx_trend_metrics_dimension ON trend_metrics (dimension_type, dimension_value);

-- =============================================================================
-- TABLE: reports
-- User-generated market intelligence reports
-- =============================================================================

CREATE TABLE reports (
    id              UUID        PRIMARY KEY DEFAULT uuid_generate_v4(),
    workspace_id    UUID        NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    created_by      UUID        NOT NULL REFERENCES users(id) ON DELETE SET NULL,
    title           VARCHAR(500) NOT NULL,
    report_type     report_type NOT NULL,
    status          report_status NOT NULL DEFAULT 'pending',
    parameters      JSONB        NOT NULL DEFAULT '{}',  -- query parameters used
    result_data     JSONB,                               -- computed result payload
    result_url      TEXT,                               -- S3 URL for large exports
    error_message   TEXT,
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    completed_at    TIMESTAMPTZ,
    updated_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE reports IS 'Async market analysis reports requested by workspace users.';

CREATE INDEX idx_reports_workspace ON reports (workspace_id);
CREATE INDEX idx_reports_status ON reports (status);
CREATE INDEX idx_reports_created ON reports (created_at DESC);

-- =============================================================================
-- TABLE: audit_logs
-- Immutable trail of all significant user actions (GDPR / compliance)
-- =============================================================================

CREATE TABLE audit_logs (
    id              UUID        PRIMARY KEY DEFAULT uuid_generate_v4(),
    workspace_id    UUID        REFERENCES workspaces(id) ON DELETE SET NULL,
    user_id         UUID        REFERENCES users(id) ON DELETE SET NULL,
    action          VARCHAR(255) NOT NULL,   -- e.g. 'report.created', 'user.invited'
    resource_type   VARCHAR(100),
    resource_id     VARCHAR(255),
    ip_address      INET,
    user_agent      TEXT,
    metadata        JSONB        NOT NULL DEFAULT '{}',
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE audit_logs IS 'Immutable event log for compliance and security auditing (GDPR Art. 30).';

CREATE INDEX idx_audit_logs_workspace ON audit_logs (workspace_id);
CREATE INDEX idx_audit_logs_user ON audit_logs (user_id);
CREATE INDEX idx_audit_logs_action ON audit_logs (action);
CREATE INDEX idx_audit_logs_created ON audit_logs (created_at DESC);

-- =============================================================================
-- TABLE: search_queries
-- Saved and anonymous search queries for analytics and UX personalisation
-- =============================================================================

CREATE TABLE search_queries (
    id              UUID        PRIMARY KEY DEFAULT uuid_generate_v4(),
    workspace_id    UUID        REFERENCES workspaces(id) ON DELETE CASCADE,
    user_id         UUID        REFERENCES users(id) ON DELETE SET NULL,
    query_text      TEXT,
    filters         JSONB        NOT NULL DEFAULT '{}',
    result_count    INTEGER,
    execution_ms    INTEGER,
    is_saved        BOOLEAN      NOT NULL DEFAULT FALSE,
    saved_name      VARCHAR(255),
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE search_queries IS 'Tracks search queries for analytics and saved-search features.';

CREATE INDEX idx_search_queries_workspace ON search_queries (workspace_id);
CREATE INDEX idx_search_queries_user ON search_queries (user_id);
CREATE INDEX idx_search_queries_created ON search_queries (created_at DESC);
CREATE INDEX idx_search_queries_saved ON search_queries (workspace_id) WHERE is_saved = TRUE;

-- =============================================================================
-- Trigger: auto-update updated_at timestamps
-- =============================================================================

CREATE OR REPLACE FUNCTION trigger_set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DO $$
DECLARE
    t TEXT;
BEGIN
    FOREACH t IN ARRAY ARRAY[
        'workspaces', 'users', 'companies', 'job_offers',
        'skills', 'salary_stats', 'reports'
    ]
    LOOP
        EXECUTE format(
            'CREATE TRIGGER set_updated_at
             BEFORE UPDATE ON %I
             FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();',
            t
        );
    END LOOP;
END;
$$;
