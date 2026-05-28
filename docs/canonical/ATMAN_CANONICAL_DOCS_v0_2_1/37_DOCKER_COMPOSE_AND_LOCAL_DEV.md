# 37 — Docker Compose and Local Development

**Project:** Atman  **Version:** v0.2.1  **Status:** Canonical / Repo-generation-ready  **Date:** 2026-05-28  **Owner:** Atman Platform Architecture
## Purpose

This document upgrades Atman from execution-grade documentation to repo-generation-ready specification. It is binding for `ATMAN_REPO_v0_3` unless superseded by a later canonical version.

## Non-negotiable invariant

```text
Atman source authority comes from reviewed corpus + provenance + citations, not from external LLM memory or unverified scraped text.
```


## Objective

`ATMAN_REPO_v0_3` must boot locally with a single Docker Compose command.

## Required services

```text
api
worker
web
studio
postgres
redis
qdrant
minio
neo4j
prometheus
grafana
```

## Local boot command

```bash
docker compose --env-file infra/.env.example -f infra/docker-compose.yml up --build
```

## Local ports

| Service | Port |
|---|---:|
| API | 8000 |
| Public web | 3000 |
| Studio | 3001 |
| Postgres | 5432 |
| Redis | 6379 |
| Qdrant | 6333 |
| MinIO | 9000/9001 |
| Neo4j | 7474/7687 |
| Grafana | 3005 |

## Minimum local workflow

```text
1. Start stack.
2. Upload seed text/PDF.
3. Parse and chunk.
4. Embed into Qdrant.
5. Run /rag/debug.
6. Ask Atman.
7. Run NyayaBench seed.
8. View result in Studio.
```

## Health requirements

```text
GET /health returns db/cache/vector/storage status
GET /version returns git sha + canonical docs version
workers expose queue depth metric
```
