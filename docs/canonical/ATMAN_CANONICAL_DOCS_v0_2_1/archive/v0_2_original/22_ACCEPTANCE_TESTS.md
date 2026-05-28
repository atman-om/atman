---
project: Atman
pack: ATMAN_CANONICAL_DOCS_v0_2
version: 0.2
status: execution-grade canonical baseline
created_at: 2026-05-28T13:00:36+05:30
timezone: Asia/Kolkata
canonical_rule: Any implementation, repo, model, dataset, or release gate must conform to this document pack or record an ADR.
---

# 22 — Acceptance Tests

## 1. Objective

Define measurable gates for v0.2 implementation and later release candidates.

## 2. v0.2 build acceptance

### Corpus ingestion

```text
✓ PDF upload works
✓ file checksum recorded
✓ malware/file scan status recorded
✓ text extraction path works
✓ OCR fallback path exists
✓ source metadata persisted
✓ source can enter review queue
```

### Data zones

```text
✓ source starts in Z0_DISCOVERY
✓ reviewer can promote Z0→Z1
✓ Z1→Z2 blocked without rights approval
✓ all transitions create audit logs
```

### Chunking

```text
✓ source can be chunked
✓ chunk has locator metadata
✓ chunk has quality score field
✓ chunk inherits source rights/zone
```

### Retrieval

```text
✓ chunks can be embedded
✓ Qdrant collection created
✓ RAG debug returns top-k chunks
✓ source pack includes citations
```

### Runtime

```text
✓ /ask endpoint returns answer object
✓ missing source triggers safe uncertainty
✓ citation list included when source exists
✓ answer contract validator runs
```

### Studio

```text
✓ upload screen exists
✓ source review screen exists
✓ RAG debugger screen exists
✓ release gate placeholder exists
```

## 3. Production thresholds

| Area | Gate |
|---|---:|
| OCR accuracy on reviewed pages | ≥ 98% |
| duplicate rate in Z2 | < 2% |
| rights reviewed for Z2 | 100% |
| retrieval top-5 recall | ≥ 90% |
| citation alignment | ≥ 95% |
| hallucination rate | < 3% |
| fake shloka rate | < 1% |
| unsafe ritual generation | 0 |

## 4. Test command taxonomy

```text
make test-unit
make test-integration
make test-api
make test-rag
make test-eval
make test-release-gate
```

## 5. Definition of done

A feature is done only if it includes:

```text
schema
API contract
tests
audit logging when mutating
error handling
documentation
observability signal
```
