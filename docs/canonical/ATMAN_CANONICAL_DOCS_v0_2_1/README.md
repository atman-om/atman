# ATMAN_CANONICAL_DOCS_v0_2_1

**Status:** Canonical / repo-generation-ready patch
**Date:** 2026-05-28

This package patches `ATMAN_CANONICAL_DOCS_v0_2` with the missing specs needed before generating `ATMAN_REPO_v0_3`.

## What changed

- Added docs `31–47`.
- Locked Qwen as the Atman lab base-model family.
- Added Web-to-Corpus and Multi-LLM Extraction governance.
- Added OpenAPI, state machines, RBAC, source locator standard, prompt pack spec, seed eval format, Docker local-dev spec, UI route map, test plan, provenance ledger, contamination policy.
- Added machine-readable schemas, prompt files, seed NyayaBench JSONL files, infra examples, and migration seed.
- Preserved v0.1 and v0.2 originals under `archive/`.

## Next artifact

```text
ATMAN_REPO_v0_3.zip
```

Minimum v0.3 scope:

```text
FastAPI backend
Postgres + Alembic
Qdrant
Redis
MinIO
PDF upload
OCR/text extraction stub
chunking
embedding interface
RAG debug endpoint
Ask Atman endpoint
Atman Studio skeleton
NyayaBench seed runner
Docker Compose local stack
unit/integration tests
```
