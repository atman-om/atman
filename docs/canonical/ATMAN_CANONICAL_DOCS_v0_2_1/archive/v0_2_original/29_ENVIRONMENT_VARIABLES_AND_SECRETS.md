---
project: Atman
pack: ATMAN_CANONICAL_DOCS_v0_2
version: 0.2
status: execution-grade canonical baseline
created_at: 2026-05-28T13:00:36+05:30
timezone: Asia/Kolkata
canonical_rule: Any implementation, repo, model, dataset, or release gate must conform to this document pack or record an ADR.
---

# 29 — Environment Variables and Secrets

## 1. Objective

Define canonical environment variables, secret classes, and handling rules.

## 2. Core environment variables

```text
ATMAN_ENV=local|dev|staging|production|airgapped_research
ATMAN_SERVICE_NAME=api|worker|rag|eval|inference
ATMAN_LOG_LEVEL=debug|info|warn|error
ATMAN_PUBLIC_BASE_URL=
ATMAN_STUDIO_BASE_URL=
```

## 3. Database and infrastructure

```text
POSTGRES_URL=
REDIS_URL=
QDRANT_URL=
QDRANT_API_KEY=
S3_ENDPOINT=
S3_BUCKET_RAW=
S3_BUCKET_ARTIFACTS=
S3_ACCESS_KEY_ID=
S3_SECRET_ACCESS_KEY=
NEO4J_URI=
NEO4J_USERNAME=
NEO4J_PASSWORD=
```

## 4. LLM provider secrets

```text
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
HF_TOKEN=
LOCAL_INFERENCE_BASE_URL=
VLLM_API_KEY=
```

## 5. Auth/security

```text
JWT_SECRET=
OIDC_ISSUER=
OIDC_CLIENT_ID=
OIDC_CLIENT_SECRET=
SESSION_SECRET=
CORS_ALLOWED_ORIGINS=
```

## 6. Observability

```text
OTEL_EXPORTER_OTLP_ENDPOINT=
PROMETHEUS_PUSHGATEWAY=
SENTRY_DSN=
GRAFANA_URL=
```

## 7. Feature flags

```text
FEATURE_PUBLIC_ASK=true|false
FEATURE_STUDIO_UPLOAD=true|false
FEATURE_SYNTHETIC_GENERATION=true|false
FEATURE_TRAINING_LAUNCH=true|false
FEATURE_RELEASE_GATE_ENFORCED=true|false
```

## 8. Secret rules

- Never commit secrets.
- `.env.example` may contain names only, never real values.
- Production secrets must use a secret manager.
- Secrets must rotate after suspected leak.
- Access to model/provider keys must be least-privilege.

## 9. Startup validation

Services must fail fast when required variables are missing for their environment.
