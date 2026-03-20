// ─────────────────────────────────────────────────────────────────────────────
// TypeScript types for the Talentora AI web application
// ─────────────────────────────────────────────────────────────────────────────

// ── Primitive helpers ─────────────────────────────────────────────────────────

export type Nullable<T> = T | null;
export type Optional<T> = T | undefined;
export type Maybe<T> = T | null | undefined;

// ── Date range ────────────────────────────────────────────────────────────────

export interface DateRange {
  from: Date;
  to: Date;
}

export type Granularity = 'day' | 'week' | 'month' | 'quarter' | 'year';

// ── Pagination ────────────────────────────────────────────────────────────────

export interface PaginationParams {
  page: number;
  pageSize: number;
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
}

// ── API response wrapper ──────────────────────────────────────────────────────

export interface ApiResponse<T> {
  data: T;
  success: boolean;
  message?: string;
  timestamp: string;
}

export interface ApiError {
  code: string;
  message: string;
  details?: Record<string, string[]>;
  timestamp: string;
}

// ── User & Auth ───────────────────────────────────────────────────────────────

export type UserRole = 'viewer' | 'analyst' | 'admin' | 'enterprise';

export type SubscriptionTier = 'starter' | 'pro' | 'team' | 'enterprise';

export type SubscriptionStatus = 'active' | 'trialing' | 'past_due' | 'canceled' | 'unpaid';

export interface User {
  id: string;
  email: string;
  name: string;
  avatarUrl: Nullable<string>;
  role: UserRole;
  organizationId: Nullable<string>;
  createdAt: string;
  updatedAt: string;
}

export interface Organization {
  id: string;
  name: string;
  logoUrl: Nullable<string>;
  plan: SubscriptionTier;
  subscriptionStatus: SubscriptionStatus;
  seats: number;
  usedSeats: number;
  createdAt: string;
}

export interface Session {
  user: User;
  organization: Nullable<Organization>;
  accessToken: string;
  expiresAt: string;
}

// ── Geography ─────────────────────────────────────────────────────────────────

export interface Country {
  code: string;          // ISO 3166-1 alpha-2
  name: string;
  region: EuropeanRegion;
  flagEmoji: string;
}

export type EuropeanRegion =
  | 'Western Europe'
  | 'Northern Europe'
  | 'Southern Europe'
  | 'Eastern Europe'
  | 'Central Europe'
  | 'Other';

export interface GeoLocation {
  country: string;
  city: Nullable<string>;
  region: Nullable<string>;
  lat: Nullable<number>;
  lng: Nullable<number>;
}

// ── Job Market ────────────────────────────────────────────────────────────────

export type ContractType =
  | 'full-time'
  | 'part-time'
  | 'contract'
  | 'freelance'
  | 'internship'
  | 'apprenticeship';

export type WorkMode = 'on-site' | 'remote' | 'hybrid';

export type ExperienceLevel = 'entry' | 'mid' | 'senior' | 'lead' | 'executive';

export interface JobOffer {
  id: string;
  title: string;
  company: Company;
  location: GeoLocation;
  contractType: ContractType;
  workMode: WorkMode;
  experienceLevel: ExperienceLevel;
  salaryMin: Nullable<number>;
  salaryMax: Nullable<number>;
  salaryCurrency: string;
  skills: string[];
  postedAt: string;
  expiresAt: Nullable<string>;
  sourceUrl: string;
  sourceName: string;
}

export interface Company {
  id: string;
  name: string;
  logoUrl: Nullable<string>;
  industry: string;
  size: CompanySize;
  country: string;
  website: Nullable<string>;
}

export type CompanySize =
  | '1-10'
  | '11-50'
  | '51-200'
  | '201-500'
  | '501-1000'
  | '1001-5000'
  | '5000+';

// ── Metrics & Analytics ───────────────────────────────────────────────────────

export interface MetricValue {
  value: number;
  change: number;           // absolute change vs previous period
  changePercent: number;    // percent change vs previous period
  trend: 'up' | 'down' | 'stable';
  period: string;           // human-readable label, e.g. "vs last month"
}

export interface TimeSeriesPoint {
  date: string;             // ISO 8601
  value: number;
  label?: string;
}

export interface TimeSeries {
  id: string;
  name: string;
  color?: string;
  data: TimeSeriesPoint[];
}

// ── Dashboard ─────────────────────────────────────────────────────────────────

export interface DashboardMetrics {
  totalJobOffers: MetricValue;
  activeCompanies: MetricValue;
  avgSalary: MetricValue;
  topSkillsDemand: MetricValue;
  newListingsToday: MetricValue;
  countriesCovered: MetricValue;
}

export interface JobTrendData {
  category: string;
  count: number;
  change: number;
  changePercent: number;
  topCountries: string[];
  topCompanies: string[];
  timeline: TimeSeriesPoint[];
}

// ── Skills ────────────────────────────────────────────────────────────────────

export interface SkillDemand {
  skill: string;
  category: SkillCategory;
  demandScore: number;      // 0-100
  jobCount: number;
  growthPercent: number;
  avgSalaryPremium: number; // % premium over baseline
  trend: TimeSeriesPoint[];
  relatedSkills: string[];
}

export type SkillCategory =
  | 'programming'
  | 'data-science'
  | 'cloud'
  | 'devops'
  | 'design'
  | 'management'
  | 'marketing'
  | 'finance'
  | 'sales'
  | 'legal'
  | 'other';

// ── Salary ────────────────────────────────────────────────────────────────────

export interface SalaryBenchmark {
  role: string;
  country: string;
  city: Nullable<string>;
  currency: string;
  p10: number;
  p25: number;
  median: number;
  p75: number;
  p90: number;
  sampleSize: number;
  updatedAt: string;
}

export interface SalaryByCountry {
  country: string;
  countryCode: string;
  median: number;
  currency: string;
  change: number;
}

// ── Reports ───────────────────────────────────────────────────────────────────

export type ReportType =
  | 'market-overview'
  | 'salary-analysis'
  | 'skill-trends'
  | 'company-intelligence'
  | 'custom';

export type ReportStatus = 'draft' | 'generating' | 'ready' | 'failed' | 'archived';

export type ReportFormat = 'pdf' | 'xlsx' | 'csv' | 'json';

export interface Report {
  id: string;
  title: string;
  type: ReportType;
  status: ReportStatus;
  format: ReportFormat;
  createdBy: string;
  createdAt: string;
  completedAt: Nullable<string>;
  downloadUrl: Nullable<string>;
  sizeBytes: Nullable<number>;
  filters: ReportFilters;
}

export interface ReportFilters {
  dateRange: DateRange;
  countries: string[];
  roles: string[];
  skills: string[];
  contractTypes: ContractType[];
  workModes: WorkMode[];
}

// ── Pricing ───────────────────────────────────────────────────────────────────

export type BillingCycle = 'monthly' | 'annual';

export interface PricingFeature {
  label: string;
  included: boolean;
  detail?: string;
}

export interface PricingTier {
  id: SubscriptionTier;
  name: string;
  tagline: string;
  monthlyPrice: Nullable<number>;   // null = custom/contact sales
  annualPrice: Nullable<number>;
  currency: string;
  seats: number | 'unlimited';
  features: PricingFeature[];
  highlighted?: boolean;
  badge?: string;
}

// ── Navigation ────────────────────────────────────────────────────────────────

export interface NavItem {
  label: string;
  href: string;
  icon?: React.ComponentType<{ className?: string }>;
  badge?: string;
  children?: NavItem[];
  external?: boolean;
}

export interface BreadcrumbItem {
  label: string;
  href?: string;
}

// ── Filter & Sort ─────────────────────────────────────────────────────────────

export type SortDirection = 'asc' | 'desc';

export interface SortConfig {
  field: string;
  direction: SortDirection;
}

export interface FilterOption<T = string> {
  label: string;
  value: T;
  count?: number;
}

// ── Chart ─────────────────────────────────────────────────────────────────────

export interface ChartConfig {
  title: string;
  subtitle?: string;
  type: 'line' | 'bar' | 'area' | 'pie' | 'donut' | 'scatter' | 'heatmap';
  granularity?: Granularity;
  series: TimeSeries[];
  xAxisLabel?: string;
  yAxisLabel?: string;
  showLegend?: boolean;
  showGrid?: boolean;
  colors?: string[];
}

// ── UI State ──────────────────────────────────────────────────────────────────

export interface LoadingState {
  isLoading: boolean;
  error: Nullable<string>;
}

export type ToastVariant = 'default' | 'success' | 'warning' | 'error' | 'info';

export interface ToastMessage {
  id: string;
  variant: ToastVariant;
  title: string;
  description?: string;
  duration?: number;
  action?: {
    label: string;
    onClick: () => void;
  };
}
