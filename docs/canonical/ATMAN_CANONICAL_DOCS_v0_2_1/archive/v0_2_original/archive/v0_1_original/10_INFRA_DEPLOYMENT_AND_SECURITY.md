# 10 — Infrastructure, Deployment, and Security

## 1. Local stack

```text
FastAPI
Next.js web
Next.js Studio
JSONL/Postgres
Qdrant
MinIO/S3
Docker Compose
```

## 2. Production stack

```text
API service: FastAPI
Workers: Celery/Temporal
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
| lab | internal experiments |
| staging | closed beta |
| production | public users |

## 4. Security controls

- auth for Atman Studio;
- RBAC for reviewers/admins;
- source upload limits;
- file scanning;
- audit logs for source/license decisions;
- rate limiting on public ask endpoint;
- model output logging with privacy redaction;
- release gate approval before production deployment.

## 5. Secrets

Secrets must not be committed.

Required secret classes:

```text
LLM provider keys
database credentials
object storage credentials
JWT/OIDC secrets
monitoring keys
```

## 6. Backup policy

Backup source registry, corpus chunks, raw uploaded PDFs, review decisions, model registry, checkpoint metadata, and release decisions.

## 7. Rollback policy

Every production release must have a previous model alias, previous RAG index snapshot, previous API image, rollback script, and release notes.
