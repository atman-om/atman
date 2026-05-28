---
project: Atman
pack: ATMAN_CANONICAL_DOCS_v0_2
version: 0.2
status: execution-grade canonical baseline
created_at: 2026-05-28T13:00:36+05:30
timezone: Asia/Kolkata
canonical_rule: Any implementation, repo, model, dataset, or release gate must conform to this document pack or record an ADR.
---

# 04 — Corpus and Data Zones

## 1. Corpus objective

ShrutiKosh converts raw Dharma sources into normalized, rights-governed, citation-addressable, retrieval-ready, training-ready, and eval-ready artifacts.

## 2. Zone definitions

| Zone | Meaning | Allowed use |
|---|---|---|
| Z0_DISCOVERY | raw discovery, rough extraction, metadata only | search/triage |
| Z1_SANDBOX | internal experiment data | lab RAG, lab FT, eval drafting |
| Z2_PRODUCTION | rights-verified, source-verified, quality-reviewed, citation-addressable | public RAG, production evals, approved training |

## 3. Artifact states

```text
INGESTED
SCANNED
PARSED
OCR_EXTRACTED
NORMALIZED
CHUNKED
CITATION_MAPPED
TAGGED
RIGHTS_REVIEW_PENDING
QUALITY_REVIEW_PENDING
APPROVED_Z1
APPROVED_Z2
INDEXED
USED_IN_DATASET
BLOCKED
DEPRECATED
DELETED
```

## 4. Source registry fields

```json
{
  "source_id": "uuid",
  "title": "Bhagavad Gita",
  "source_type": "book|pdf|web|note|synthetic",
  "language": "hi|sa|en|mixed",
  "rights_status": "PUBLIC_DOMAIN_VERIFIED",
  "zone": "Z2_PRODUCTION",
  "checksum_sha256": "...",
  "citation_scheme": "work.chapter.verse",
  "review_status": "approved",
  "created_at": "..."
}
```

## 5. Source addressability

Every production chunk must have stable locator metadata:

```text
work
book/kanda/parva/chapter
verse/shloka/section
commentary identifier
translation identifier
page number when applicable
edition
publisher/source URL when applicable
source locator string
```

## 6. Promotion rules

### Z0 → Z1

Requires:

- basic parse success;
- no malware/file safety issue;
- rights status not `NO_STORAGE_ALLOWED`;
- metadata record exists.

### Z1 → Z2

Requires:

- rights status allows intended use;
- source locator valid;
- quality review approved;
- duplicate/similarity check passed;
- citation addressability complete;
- reviewer identity recorded.

## 7. Synthetic data constraint

Synthetic data may be stored in Z1 for draft/training experiments. It may never become scripture authority. Any synthetic item promoted to production must be labeled as synthetic explanatory data, not source text.
