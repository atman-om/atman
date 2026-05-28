---
project: Atman
pack: ATMAN_CANONICAL_DOCS_v0_2
version: 0.2
status: execution-grade canonical baseline
created_at: 2026-05-28T13:00:36+05:30
timezone: Asia/Kolkata
canonical_rule: Any implementation, repo, model, dataset, or release gate must conform to this document pack or record an ADR.
---

# 05 — RAG and Retrieval Specification

## 1. Objective

The RAG layer provides source-grounded knowledge to Atman Acharya. It must retrieve, rank, cite, and validate evidence before answer release.

## 2. Retrieval architecture

```text
query
→ language/script normalization
→ intent expansion
→ BM25 lexical retrieval
→ dense vector retrieval
→ TattvaNet graph expansion
→ reranker
→ source-pack builder
→ citation verifier
```

## 3. Chunking rules

| Source type | Chunk unit |
|---|---|
| Gita/verse text | verse + immediate context |
| commentary | paragraph + linked verse |
| prose scripture | semantic section |
| long PDF | heading-aware 300–700 tokens |
| QA/explanation | complete answer block |

## 4. Chunk metadata

```json
{
  "chunk_id": "uuid",
  "source_id": "uuid",
  "chunk_text": "...",
  "language": "hi",
  "script": "devanagari",
  "locator": {
    "work": "Bhagavad Gita",
    "chapter": "2",
    "verse": "47"
  },
  "rights_status": "PUBLIC_DOMAIN_VERIFIED",
  "zone": "Z2_PRODUCTION",
  "quality_score": 0.97
}
```

## 5. Retrieval thresholds

| Metric | Production target |
|---|---:|
| top-5 recall on golden set | ≥ 90% |
| citation alignment | ≥ 95% |
| source-pack precision | ≥ 85% |
| no-source refusal correctness | ≥ 95% |
| average retrieval latency | ≤ 800 ms internal target |

## 6. Source-pack rules

A source pack must include:

```json
{
  "query_id": "uuid",
  "chunks": [],
  "coverage": "none|partial|strong",
  "citation_candidates": [],
  "risk_flags": [],
  "allowed_answer_mode": "answer|partial|refuse"
}
```

## 7. No-source handling

If coverage is `none`, the runtime must not invent scripture or doctrine. It must answer with uncertainty or request a source expansion path.

## 8. Index rebuild rules

Production RAG indexes are immutable snapshots. New indexes are built as candidate snapshots and released only through `RAG_INDEX` release gate.
