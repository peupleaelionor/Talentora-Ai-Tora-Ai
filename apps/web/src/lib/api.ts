import { type ApiResponse, type ApiError } from '@/types';

// ─────────────────────────────────────────────────────────────────────────────
// Configuration
// ─────────────────────────────────────────────────────────────────────────────

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000';

const DEFAULT_TIMEOUT_MS = 30_000;

// ─────────────────────────────────────────────────────────────────────────────
// Custom errors
// ─────────────────────────────────────────────────────────────────────────────

export class ApiRequestError extends Error {
  constructor(
    public readonly status: number,
    public readonly error: ApiError
  ) {
    super(error.message);
    this.name = 'ApiRequestError';
  }
}

export class NetworkError extends Error {
  constructor(message = 'Network request failed') {
    super(message);
    this.name = 'NetworkError';
  }
}

export class TimeoutError extends Error {
  constructor() {
    super(`Request timed out after ${DEFAULT_TIMEOUT_MS}ms`);
    this.name = 'TimeoutError';
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// Request helpers
// ─────────────────────────────────────────────────────────────────────────────

interface RequestOptions extends Omit<RequestInit, 'body'> {
  body?: unknown;
  params?: Record<string, string | number | boolean | undefined | null>;
  timeout?: number;
}

function buildUrl(
  path: string,
  params?: Record<string, string | number | boolean | undefined | null>
): string {
  const url = new URL(path, API_BASE_URL);
  if (params) {
    for (const [key, value] of Object.entries(params)) {
      if (value !== undefined && value !== null) {
        url.searchParams.set(key, String(value));
      }
    }
  }
  return url.toString();
}

async function request<T>(
  path: string,
  options: RequestOptions = {}
): Promise<ApiResponse<T>> {
  const { body, params, timeout = DEFAULT_TIMEOUT_MS, headers, ...rest } = options;

  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeout);

  const url = buildUrl(path, params);

  const requestHeaders: HeadersInit = {
    'Content-Type': 'application/json',
    Accept: 'application/json',
    ...(headers as Record<string, string>),
  };

  try {
    const response = await fetch(url, {
      ...rest,
      headers: requestHeaders,
      signal: controller.signal,
      body: body !== undefined ? JSON.stringify(body) : undefined,
    });

    clearTimeout(timeoutId);

    if (!response.ok) {
      let errorBody: ApiError;
      try {
        errorBody = await response.json();
      } catch {
        errorBody = {
          code: `HTTP_${response.status}`,
          message: response.statusText || 'Request failed',
          timestamp: new Date().toISOString(),
        };
      }
      throw new ApiRequestError(response.status, errorBody);
    }

    return response.json() as Promise<ApiResponse<T>>;
  } catch (err) {
    clearTimeout(timeoutId);
    if (err instanceof ApiRequestError) throw err;
    if (err instanceof DOMException && err.name === 'AbortError') {
      throw new TimeoutError();
    }
    throw new NetworkError(err instanceof Error ? err.message : undefined);
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// HTTP verbs
// ─────────────────────────────────────────────────────────────────────────────

export const api = {
  get<T>(path: string, options?: Omit<RequestOptions, 'method' | 'body'>) {
    return request<T>(path, { ...options, method: 'GET' });
  },
  post<T>(path: string, body?: unknown, options?: Omit<RequestOptions, 'method'>) {
    return request<T>(path, { ...options, method: 'POST', body });
  },
  put<T>(path: string, body?: unknown, options?: Omit<RequestOptions, 'method'>) {
    return request<T>(path, { ...options, method: 'PUT', body });
  },
  patch<T>(path: string, body?: unknown, options?: Omit<RequestOptions, 'method'>) {
    return request<T>(path, { ...options, method: 'PATCH', body });
  },
  delete<T>(path: string, options?: Omit<RequestOptions, 'method'>) {
    return request<T>(path, { ...options, method: 'DELETE' });
  },
};

// ─────────────────────────────────────────────────────────────────────────────
// Domain-specific API helpers
// ─────────────────────────────────────────────────────────────────────────────

import type {
  DashboardMetrics,
  JobTrendData,
  SkillDemand,
  SalaryBenchmark,
  Report,
  PaginatedResponse,
  PaginationParams,
} from '@/types';

export const dashboardApi = {
  getMetrics: () => api.get<DashboardMetrics>('/api/v1/dashboard/metrics'),
};

export const jobsApi = {
  getTrends: (params?: Record<string, string | number | boolean | undefined | null>) =>
    api.get<JobTrendData[]>('/api/v1/jobs/trends', { params }),
};

export const skillsApi = {
  getDemand: (params?: Record<string, string | number | boolean | undefined | null>) =>
    api.get<SkillDemand[]>('/api/v1/skills/demand', { params }),
};

export const salaryApi = {
  getBenchmarks: (params?: Record<string, string | number | boolean | undefined | null>) =>
    api.get<SalaryBenchmark[]>('/api/v1/salary/benchmarks', { params }),
};

export const reportsApi = {
  list: (pagination: PaginationParams) =>
    api.get<PaginatedResponse<Report>>('/api/v1/reports', {
      params: { page: pagination.page, pageSize: pagination.pageSize },
    }),
  create: (payload: Partial<Report>) =>
    api.post<Report>('/api/v1/reports', payload),
  delete: (id: string) =>
    api.delete<void>(`/api/v1/reports/${id}`),
};

// ─────────────────────────────────────────────────────────────────────────────
// Auth helpers
// ─────────────────────────────────────────────────────────────────────────────

export const authApi = {
  login: (email: string, password: string) =>
    api.post<{ accessToken: string; refreshToken: string }>('/api/v1/auth/login', {
      email,
      password,
    }),
  logout: () => api.post<void>('/api/v1/auth/logout'),
  refreshToken: (refreshToken: string) =>
    api.post<{ accessToken: string }>('/api/v1/auth/refresh', { refreshToken }),
  me: () => api.get<import('@/types').User>('/api/v1/auth/me'),
};
