# Security Hardening

## Required before real production

- Replace default JWT secret.
- Enable auth/RBAC.
- Restrict CORS origins.
- Put API behind TLS reverse proxy.
- Disable force crawl for normal users.
- Store secrets in a secret manager.
- Enable audit log export.
- Add WAF/rate-limit on public endpoints.
