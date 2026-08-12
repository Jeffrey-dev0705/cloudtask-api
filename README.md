# CloudTask API

Multi-tenant async job API: FastAPI, PostgreSQL, Redis, Celery. Optional Prometheus/Grafana, Docker Compose, and Kubernetes manifests.

## Architecture

```mermaid
flowchart TB
  subgraph clients [Clients]
    Human[JWT client]
    Machine[API-key client]
  end
  Human --> API[FastAPI]
  Machine --> API
  API --> PG[(PostgreSQL)]
  API --> Redis[(Redis)]
  Redis --> Worker[Celery worker]
  Worker --> PG
  Worker --> Hook[HMAC webhooks]
  Prom[Prometheus] -->|scrape /metrics| API
  Graf[Grafana] --> Prom
```

## Auth flow

```mermaid
sequenceDiagram
  participant U as User
  participant API as FastAPI
  participant DB as PostgreSQL
  participant M as Machine client
  U->>API: POST /api/v1/auth/register or /login
  API->>DB: create or verify user
  API-->>U: access + refresh JWT
  U->>API: POST /api/v1/organizations
  API-->>U: organization id
  U->>API: Bearer + X-Organization-ID
  Note over U,API: owner/admin can create API keys and webhooks
  M->>API: X-API-Key on POST /api/v1/service/jobs
```

## Job lifecycle

```mermaid
stateDiagram-v2
  [*] --> queued: persist then enqueue
  queued --> running: worker starts
  queued --> cancelled: cancel before run
  running --> completed: success
  running --> failed: error or retries exhausted
  failed --> running: Celery retry if attempts remain
  completed --> [*]
  cancelled --> [*]
  failed --> [*]
```

On `completed` / `failed`, the worker may POST signed webhooks (`job.completed`, `job.failed`).

## Features

- JWT access/refresh tokens; hashed, revocable API keys
- Organizations with owner/admin/member roles
- Tenant-scoped jobs: create, list, get, retry, cancel; idempotency keys
- Celery workers with attempt history and bounded retries
- HMAC-SHA256 webhook deliveries with delivery records
- Redis fixed-window rate limiting
- `/health`, `/ready`, `/metrics`
- Docker Compose, GitHub Actions CI, Kubernetes + HPA

## Quick start

```bash
cp .env.example .env
docker compose up -d --build
docker compose exec api alembic upgrade head
```

If no migration exists yet:

```bash
docker compose exec api alembic revision --autogenerate -m "initial schema"
docker compose exec api alembic upgrade head
```

| Service | URL |
|---------|-----|
| Swagger | http://localhost:8000/docs |
| Metrics | http://localhost:8000/metrics |
| Prometheus | http://localhost:9090 |
| Grafana | http://localhost:3000 (`admin` / `admin`, local only) |

Core stack without monitoring:

```bash
docker compose up -d --build api worker postgres redis
```

## API overview

| Area | Prefix | Auth |
|------|--------|------|
| Auth | `/api/v1/auth` | public register/login/refresh |
| Orgs | `/api/v1/organizations` | JWT |
| Jobs | `/api/v1/jobs` | JWT + `X-Organization-ID` |
| API keys | `/api/v1/api-keys` | JWT + org; owner/admin |
| Webhooks | `/api/v1/webhooks` | JWT + org; owner/admin |
| Service jobs | `/api/v1/service/jobs` | `X-API-Key` |

## Webhooks

Events: `job.completed`, `job.failed`.

Delivery headers:

- `X-CloudTask-Event`
- `X-CloudTask-Signature` — HMAC-SHA256 of the raw JSON body

## Layout

```text
app/            API, models, schemas, Celery workers
alembic/        DB migrations
monitoring/     Prometheus + Grafana
deploy/         Kubernetes manifests; Terraform notes
docs/           architecture and security notes
tests/          unit tests
```

## Docs

- [Architecture](docs/architecture.md)
- [Security](docs/security.md)

## Limitations

- Service-job `created_by` is set to an org owner when no user is on the API key
- Terraform under `deploy/terraform/` is notes only (no modules yet)
- `AuditLog` model exists but is not wired into request handlers
