# 31 — OpenAPI Specification

**Project:** Atman  **Version:** v0.2.1  **Status:** Canonical / Repo-generation-ready  **Date:** 2026-05-28  **Owner:** Atman Platform Architecture
## Purpose

This document upgrades Atman from execution-grade documentation to repo-generation-ready specification. It is binding for `ATMAN_REPO_v0_3` unless superseded by a later canonical version.

## Non-negotiable invariant

```text
Atman source authority comes from reviewed corpus + provenance + citations, not from external LLM memory or unverified scraped text.
```


## Scope

This file defines the canonical HTTP surface that must be implemented in `services/api` and mirrored by `schemas/openapi.yaml`.

## API principles

```text
1. Every write endpoint is authenticated.
2. Every corpus/release/training write endpoint is audit-logged.
3. Every state-changing endpoint is idempotent or explicitly non-idempotent.
4. Every list endpoint supports pagination.
5. Every generated answer returns trace/citation metadata.
6. Every unsafe/failing answer returns a blocked response, not a silent hallucination.
```

## Standard envelope

### Success

```json
{
  "ok": true,
  "data": {},
  "meta": {
    "request_id": "req_...",
    "trace_id": "trc_...",
    "version": "v0.2.1"
  }
}
```

### Error

```json
{
  "ok": false,
  "error": {
    "code": "ATMAN_VALIDATION_ERROR",
    "message": "Human-readable failure.",
    "details": {}
  },
  "meta": {
    "request_id": "req_..."
  }
}
```

## Auth model

| Endpoint family | Required role |
|---|---|
| `/public/*` | anonymous allowed |
| `/ask/*` | user/session |
| `/sources/*` | corpus_editor+ |
| `/rights/*` | rights_reviewer+ |
| `/ontology/*` | ontology_editor+ |
| `/datasets/*` | dataset_editor+ |
| `/models/*` | ml_engineer+ |
| `/release/*` | release_manager+ |
| `/admin/*` | admin |

## Endpoint families

### Health

```http
GET /health
GET /version
```

### Source ingestion

```http
POST /sources
GET /sources
GET /sources/{source_id}
POST /sources/{source_id}/files
POST /sources/{source_id}/parse
POST /sources/{source_id}/chunk
POST /sources/{source_id}/review
POST /sources/{source_id}/promote
POST /sources/{source_id}/deprecate
```

### Web-to-corpus

```http
POST /web/crawl-jobs
GET /web/crawl-jobs
GET /web/crawl-jobs/{job_id}
POST /web/sources/{web_source_id}/extract
POST /web/sources/{web_source_id}/rights-review
POST /web/sources/{web_source_id}/promote
```

### RAG / Ask Atman

```http
POST /ask
POST /rag/debug
POST /rag/retrieve
POST /rag/rerank
POST /rag/verify-citations
```

### Content factory

```http
POST /content/jobs
GET /content/jobs
GET /content/jobs/{job_id}
POST /content/jobs/{job_id}/approve
POST /content/jobs/{job_id}/reject
POST /content/export
```

### Eval / release

```http
POST /eval/runs
GET /eval/runs
GET /eval/runs/{run_id}
POST /release/gates
POST /release/gates/{gate_id}/approve
POST /release/gates/{gate_id}/reject
POST /release/gates/{gate_id}/rollback
```

## Required headers

| Header | Required | Purpose |
|---|---:|---|
| `Authorization` | write endpoints | JWT/session token |
| `X-Request-Id` | recommended | trace correlation |
| `Idempotency-Key` | write endpoints | duplicate prevention |
| `X-Atman-Env` | internal | environment tag |

## Pagination

```json
{
  "page": 1,
  "page_size": 50,
  "total": 290,
  "next_cursor": "cur_..."
}
```

## Error code registry

| Code | Meaning |
|---|---|
| `ATMAN_AUTH_REQUIRED` | missing auth |
| `ATMAN_FORBIDDEN` | insufficient role |
| `ATMAN_VALIDATION_ERROR` | request schema failed |
| `ATMAN_STATE_TRANSITION_BLOCKED` | illegal lifecycle move |
| `ATMAN_RIGHTS_BLOCKED` | rights policy blocks action |
| `ATMAN_SOURCE_NOT_FOUND` | source id invalid |
| `ATMAN_CITATION_FAILED` | citation verification failed |
| `ATMAN_RELEASE_GATE_FAILED` | release not allowed |
| `ATMAN_RATE_LIMITED` | rate limit exceeded |

## Acceptance criteria

```text
✓ schemas/openapi.yaml validates with OpenAPI 3.1 parser
✓ all implemented routes match this doc
✓ all write endpoints produce audit log
✓ every endpoint returns standard envelope
✓ idempotent endpoints deduplicate identical idempotency keys
```
