# 45 — Corpus Provenance Ledger

**Project:** Atman  **Version:** v0.2.1  **Status:** Canonical / Repo-generation-ready  **Date:** 2026-05-28  **Owner:** Atman Platform Architecture
## Purpose

This document upgrades Atman from execution-grade documentation to repo-generation-ready specification. It is binding for `ATMAN_REPO_v0_3` unless superseded by a later canonical version.

## Non-negotiable invariant

```text
Atman source authority comes from reviewed corpus + provenance + citations, not from external LLM memory or unverified scraped text.
```


## Purpose

Every corpus artifact must be traceable from source acquisition to runtime answer.

## Ledger events

```text
SOURCE_REGISTERED
FILE_UPLOADED
WEB_CRAWLED
TEXT_EXTRACTED
OCR_CORRECTED
CHUNK_CREATED
RIGHTS_REVIEWED
QUALITY_REVIEWED
EMBEDDED
INDEXED
USED_IN_ANSWER
USED_IN_DATASET
USED_IN_TRAINING
DEPRECATED
REVOKED
```

## Event schema

```json
{
  "event_id": "evt_...",
  "artifact_type": "source|chunk|dataset|model|answer",
  "artifact_id": "uuid",
  "event_type": "CHUNK_CREATED",
  "actor_type": "human|system|agent",
  "actor_id": "uuid|service_name",
  "timestamp": "2026-05-28T00:00:00+05:30",
  "previous_state": "NORMALIZED",
  "next_state": "CHUNKED",
  "hash_before": "sha256:...",
  "hash_after": "sha256:...",
  "reason": "chunking pipeline completed"
}
```

## Answer provenance

Every answer stores:

```text
query
retrieved chunk ids
reranked chunk ids
citation locators
model id
prompt pack id
safety decision
answer hash
feedback id if any
```

## Ledger immutability

```text
append-only by default
corrections are new events
physical deletion requires legal/security workflow
```
