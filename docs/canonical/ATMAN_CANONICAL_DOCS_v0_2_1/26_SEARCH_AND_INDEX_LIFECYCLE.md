---
project: Atman
pack: ATMAN_CANONICAL_DOCS_v0_2
version: 0.2
status: execution-grade canonical baseline
created_at: 2026-05-28T13:00:36+05:30
timezone: Asia/Kolkata
canonical_rule: Any implementation, repo, model, dataset, or release gate must conform to this document pack or record an ADR.
---

# 26 — Search and Index Lifecycle

## 1. Objective

Define the lifecycle for lexical, vector, and graph search indexes.

## 2. Index pipeline

```text
ingest
→ normalize
→ chunk
→ citation map
→ embed
→ validate
→ index candidate
→ run retrieval eval
→ approve release gate
→ promote index alias
→ monitor
→ refresh
→ deprecate
```

## 3. Retrieval stack

```text
BM25 lexical retrieval
+
dense vector retrieval
+
TattvaNet graph expansion
+
cross-encoder reranking
+
citation validator
```

## 4. Collection naming

```text
atman_chunks_z1_lab_vYYYYMMDD_N
atman_chunks_z2_prod_candidate_vYYYYMMDD_N
atman_chunks_z2_prod_vYYYYMMDD_N
```

## 5. Index manifest

```json
{
  "index_id": "uuid",
  "index_type": "qdrant_dense",
  "collection_name": "atman_chunks_z2_prod_v20260528_1",
  "embedding_model": "...",
  "chunk_snapshot_hash": "...",
  "chunk_count": 125000,
  "created_at": "..."
}
```

## 6. Promotion rule

Production alias changes only through release gate.

```text
candidate index passes retrieval gold
→ citation alignment passes
→ no RED/blocked chunks
→ release manager approval
→ alias updated
```

## 7. Refresh policy

| Trigger | Action |
|---|---|
| new Z2 source batch | build candidate index |
| embedding model change | full rebuild |
| chunking strategy change | full rebuild |
| rights revocation | emergency de-index |
| degraded retrieval | investigate + rerun retrieval eval |

## 8. Deprecation

Old indexes are retained until rollback window ends. Deleting an index requires retention policy approval.
