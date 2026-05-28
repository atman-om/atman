---
project: Atman
pack: ATMAN_CANONICAL_DOCS_v0_2
version: 0.2
status: execution-grade canonical baseline
created_at: 2026-05-28T13:00:36+05:30
timezone: Asia/Kolkata
canonical_rule: Any implementation, repo, model, dataset, or release gate must conform to this document pack or record an ADR.
---

# 10 — Infrastructure, Deployment, and Security Baseline

## 1. Local stack

```text
FastAPI
Next.js web
Next.js Studio
PostgreSQL
Qdrant
MinIO/S3
Redis
Docker Compose
```

## 2. Production stack

```text
API service: FastAPI
Workers: Celery/Temporal/Dramatiq
DB: PostgreSQL
Vector DB: Qdrant
Object store: S3/MinIO
LLM serving: vLLM/SGLang/Ollama/OpenAI-compatible adapter
Frontend: Next.js
Monitoring: Prometheus/Grafana/OpenTelemetry
Auth: OIDC/RBAC
```

## 3. Environments

| Environment | Purpose |
|---|---|
| local | development |
| dev | shared engineering |
| staging | closed beta/release candidates |
| production | public users |
| airgapped_research | restricted/offline experiments |

## 4. CI/CD required checks

```text
format
lint
typecheck
unit_tests
integration_tests
migration_check
security_scan
container_scan
eval_gate
artifact_signing
```

## 5. Backup policy

Backup source registry, corpus chunks, raw uploaded PDFs, review decisions, model registry, checkpoint metadata, eval results, and release decisions.

## 6. Rollback policy

Every production release must have:

```text
previous model alias
previous RAG index snapshot
previous prompt pack
previous API image
rollback command
release notes
```
