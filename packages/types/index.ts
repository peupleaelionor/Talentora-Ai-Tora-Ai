/**
 * Shared TypeScript types for Talentora AI platform.
 */

// ─── Enums ────────────────────────────────────────────────────────────────────

export type Plan = "starter" | "pro" | "team" | "enterprise";
export type BillingStatus = "active" | "trialing" | "past_due" | "canceled" | "unpaid";
export type RemoteType = "remote" | "onsite" | "hybrid" | "unknown";
export type ContractType = "cdi" | "cdd" | "freelance" | "internship" | "apprenticeship" | "other";
export type ExperienceLevel = "junior" | "mid" | "senior" | "lead" | "executive" | "unknown";
export type SeniorityLevel = "junior" | "mid" | "senior" | "staff" | "principal" | "director" | "vp" | "c-level";
export type JobStatus = "active" | "expired" | "filled" | "draft";
export type ReportFormat = "pdf" | "html" | "csv" | "json";
export type TrendDirection = "up" | "down" | "stable";
export type UserRole = "owner" | "admin" | "analyst" | "viewer";

// ─── Core Entities ─────────────────────────────────────────────────────────────

export interface JobOffer {
  id: string;
  source: string;
  source_job_id: string | null;
  title: string;
  company_name: string;
  company_id: string | null;
  company_size: string | null;
  industry: string | null;
  location_city: string | null;
  location_region: string | null;
  location_country: string | null;
  remote_type: RemoteType;
  contract_type: ContractType;
  salary_min: number | null;
  salary_max: number | null;
  salary_currency: string | null;
  experience_level: ExperienceLevel;
  seniority: SeniorityLevel | null;
  description_raw: string | null;
  description_clean: string | null;
  skills_raw: string[];
  skills_normalized: string[];
  technologies: string[];
  keywords: string[];
  responsibilities: string[];
  benefits: string[];
  posted_at: string | null;
  scraped_at: string;
  application_url: string | null;
  source_url: string | null;
  language: string | null;
  status: JobStatus;
  dedupe_hash: string | null;
  created_at: string;
  updated_at: string;
}

export interface Company {
  id: string;
  name: string;
  website: string | null;
  industry: string | null;
  size: string | null;
  country: string | null;
  region: string | null;
  city: string | null;
  hiring_signals: Record<string, unknown> | null;
  career_page_url: string | null;
  linkedin_url: string | null;
  enriched_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface Skill {
  id: string;
  name: string;
  normalized_name: string;
  category: string | null;
  aliases: string[];
  confidence: number;
  created_at: string;
  updated_at: string;
}

export interface JobSkill {
  job_offer_id: string;
  skill_id: string;
  confidence: number;
  source_type: "rule" | "nlp" | "embedding" | "manual";
}

export interface SalaryStats {
  id: string;
  role: string;
  region: string | null;
  seniority: string | null;
  min: number;
  median: number;
  max: number;
  count: number;
  computed_at: string;
}

export interface TrendMetric {
  id: string;
  metric_type: string;
  dimension: string;
  value: number;
  timeframe: string;
  confidence: number;
  computed_at: string;
}

export interface Report {
  id: string;
  title: string;
  audience: string | null;
  summary: string | null;
  generated_at: string;
  file_url: string | null;
  format: ReportFormat;
  pricing_tier: Plan | null;
  workspace_id: string | null;
}

export interface Workspace {
  id: string;
  name: string;
  plan: Plan;
  billing_status: BillingStatus;
  settings: Record<string, unknown>;
  stripe_customer_id: string | null;
  created_at: string;
  updated_at: string;
}

export interface User {
  id: string;
  email: string;
  full_name: string | null;
  role: UserRole;
  workspace_id: string;
  is_active: boolean;
  preferences: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export interface AuditLog {
  id: string;
  event_type: string;
  actor_id: string | null;
  workspace_id: string | null;
  metadata: Record<string, unknown>;
  created_at: string;
}

// ─── API Response Types ────────────────────────────────────────────────────────

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  per_page: number;
  pages: number;
}

export interface ApiError {
  detail: string;
  code?: string;
  field?: string;
}

export interface ApiResponse<T> {
  data: T;
  meta?: Record<string, unknown>;
}

// ─── Analytics Types ──────────────────────────────────────────────────────────

export interface SkillTrend {
  skill_name: string;
  current_count: number;
  previous_count: number;
  growth_rate: number;
  direction: TrendDirection;
  timeframe: string;
  region: string | null;
}

export interface DashboardMetrics {
  total_jobs: number;
  total_companies: number;
  total_skills: number;
  new_jobs_today: number;
  new_jobs_week: number;
  avg_salary_min: number | null;
  avg_salary_max: number | null;
  top_skills: SkillTrend[];
  top_locations: { location: string; count: number }[];
}

// ─── Search Types ─────────────────────────────────────────────────────────────

export interface SearchFilters {
  query?: string;
  location?: string;
  region?: string;
  country?: string;
  remote_type?: RemoteType;
  contract_type?: ContractType;
  experience_level?: ExperienceLevel;
  skills?: string[];
  salary_min?: number;
  salary_max?: number;
  posted_after?: string;
  posted_before?: string;
  source?: string;
  page?: number;
  per_page?: number;
  sort_by?: "relevance" | "date" | "salary" | "trend_score";
  sort_order?: "asc" | "desc";
}
