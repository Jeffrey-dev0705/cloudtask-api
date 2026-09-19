# Security

- Humans: short-lived JWT access tokens plus longer-lived refresh tokens (`Authorization: Bearer`).
- Machines: API keys (`X-API-Key`). Raw `ctk_…` secret is returned once; only a SHA-256 hash is stored. Keys are revocable and may expire.
- Tenancy: every org-scoped route requires membership. Creating/listing API keys and webhooks requires `owner` or `admin`.
- Webhooks: `X-CloudTask-Signature` is HMAC-SHA256 over the raw request body; verify before trusting the event.
- Rate limit: Redis fixed-window per client IP. If Redis is unreachable, the limiter fails open (requests are allowed).
- Config secrets (`JWT_SECRET_KEY`, `DATABASE_URL`, etc.) stay in env / secret stores, not in Git. Use `secret.example.yaml` as a template only.