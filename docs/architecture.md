# Architecture

See the system, auth, and job-lifecycle diagrams in the [README](../README.md).

## Data path

1. API accepts a job (JWT + org header, or API key).
2. Job row is written to PostgreSQL (`queued`), then enqueued on Redis via Celery.
3. Worker loads the job, records a `JobAttempt`, runs work, updates status.
4. On terminal success/failure, matching webhooks are delivered with HMAC signatures.

## Reliability

- Persist the job before enqueue so a crash after DB commit can still be reconciled.
- Optional `Idempotency-Key` avoids duplicate creates on client retries.
- Celery late ack + exponential backoff; attempts are stored separately from the job row.
- Tenant access is enforced via organization membership (and roles for keys/webhooks).
- `/health` is liveness; `/ready` checks PostgreSQL and Redis for orchestration probes.