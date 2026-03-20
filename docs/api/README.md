# API Reference

## Base URL
```
Production:  https://api.talentora.ai/api/v1
Development: http://localhost:8000/api/v1
```
Interactive docs: `GET /docs` (Swagger UI), `GET /redoc`

## Authentication
JWT Bearer token. Obtain via `/auth/login`.
```
Authorization: Bearer <access_token>
```

## Endpoints

### Auth
| Method | Path | Description |
|--------|------|-------------|
| POST | /auth/register | Create account |
| POST | /auth/login | Obtain JWT |
| POST | /auth/refresh | Refresh token |
| GET  | /auth/me | Current user |

**POST /auth/login**
```json
// Request
{ "email": "user@example.com", "password": "secret" }
// Response 200
{ "access_token": "eyJ...", "token_type": "bearer", "expires_in": 1800 }
```

### Jobs
| Method | Path | Description |
|--------|------|-------------|
| GET | /jobs | Search/filter job offers |
| GET | /jobs/{id} | Job detail |
| GET | /jobs/stats/summary | Aggregated counts |

**GET /jobs** query params: `q`, `city`, `region`, `contract_type`, `experience_level`, `salary_min`, `salary_max`, `remote_policy`, `skills`, `page`, `per_page`

```json
// Response 200
{
  "items": [{ "id": "uuid", "title": "...", "company_name": "...", "salary_min": 55000 }],
  "total": 1523,
  "page": 1,
  "per_page": 20
}
```

### Analytics
| Method | Path | Description |
|--------|------|-------------|
| GET | /analytics/salary | Salary benchmarks |
| GET | /analytics/skills/trending | Trending skills |
| GET | /analytics/market/heatmap | Geographic demand |
| GET | /analytics/trends | Time-series trends |

**GET /analytics/salary** params: `title`, `region`, `experience_level`
```json
{
  "p10": 42000, "p25": 52000, "median": 65000,
  "p75": 80000, "p90": 95000, "sample_size": 342
}
```

### Reports
| Method | Path | Description |
|--------|------|-------------|
| POST | /reports | Create async report |
| GET  | /reports | List workspace reports |
| GET  | /reports/{id} | Report status/result |

### Billing
| Method | Path | Description |
|--------|------|-------------|
| GET  | /billing/plans | Available plans |
| POST | /billing/checkout | Create Stripe session |
| POST | /billing/webhook | Stripe webhook (internal) |
| GET  | /billing/subscription | Current subscription |

## Error Codes
| Code | Meaning |
|------|---------|
| 400 | Validation error |
| 401 | Unauthenticated |
| 403 | Insufficient plan/permission |
| 404 | Resource not found |
| 422 | Unprocessable entity |
| 429 | Rate limit exceeded |
| 500 | Internal server error |

```json
// Error response shape
{ "detail": "Human-readable message", "code": "RATE_LIMIT_EXCEEDED" }
```

## Rate Limiting
| Plan | Requests/minute |
|------|----------------|
| Free | 20 |
| Starter | 100 |
| Pro | 500 |
| Team | 2000 |

Headers returned: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`
