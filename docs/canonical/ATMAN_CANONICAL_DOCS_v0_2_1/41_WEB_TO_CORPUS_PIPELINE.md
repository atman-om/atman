# 41 — Web-to-Corpus Pipeline

**Project:** Atman  **Version:** v0.2.1  **Status:** Canonical / Repo-generation-ready  **Date:** 2026-05-28  **Owner:** Atman Platform Architecture
## Purpose

This document upgrades Atman from execution-grade documentation to repo-generation-ready specification. It is binding for `ATMAN_REPO_v0_3` unless superseded by a later canonical version.

## Non-negotiable invariant

```text
Atman source authority comes from reviewed corpus + provenance + citations, not from external LLM memory or unverified scraped text.
```


## Purpose

Atman may ingest web-accessible material only through a governed pipeline.

## Pipeline

```text
seed_url
→ robots/tos check
→ crawl snapshot
→ content extraction
→ boilerplate removal
→ language detection
→ duplicate detection
→ rights classification
→ LLM-assisted structuring
→ claim/evidence mapping
→ review
→ Z1 sandbox
→ Z2 production if approved
→ RAG index
```

## Allowed sources

```text
public-domain texts
open-license material
official publisher pages with allowed access
user-owned or user-provided web pages
reference-only pages marked non-training
```

## Forbidden sources

```text
paywalled pages without permission
login-gated pages without permission
sites disallowing crawl/use under robots or ToS policy
pirated PDFs/books
content with unclear ownership promoted directly to training
```

## Web source record

```json
{
  "web_source_id": "web_...",
  "url": "https://example.org/page",
  "retrieved_at": "2026-05-28T00:00:00+05:30",
  "robots_status": "allowed",
  "tos_status": "allowed",
  "rights_status": "OPEN_LICENSE_VERIFIED",
  "content_hash": "sha256:...",
  "allowed_usage": {
    "store": true,
    "rag": true,
    "train": false,
    "quote": "limited"
  }
}
```

## LLM-assisted extraction boundary

```text
LLMs may extract headings, claims, concepts, Q&A candidates, and metadata.
LLMs may not become the cited source.
LLM output is draft annotation until verified against source spans.
```
