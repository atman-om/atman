---
project: Atman
pack: ATMAN_CANONICAL_DOCS_v0_2
version: 0.2
status: execution-grade canonical baseline
created_at: 2026-05-28T13:00:36+05:30
timezone: Asia/Kolkata
canonical_rule: Any implementation, repo, model, dataset, or release gate must conform to this document pack or record an ADR.
---

# 02 — System Architecture

## 1. Architecture principle

Atman is a layered system:

```text
Corpus → Ontology/RAG → Model behavior → Runtime verification → Monitoring loop
```

Knowledge must not live only inside model weights.

## 2. High-level architecture

```text
[Sources]
  ├─ PDFs/books
  ├─ web references
  ├─ public-domain texts
  ├─ licensed texts
  ├─ teacher-model-assisted draft data
  └─ human-written explanations
        ↓
[ShrutiKosh Corpus Agent]
        ↓
[Z0 Discovery | Z1 Sandbox | Z2 Production]
        ↓
[TattvaNet + Qdrant RAG]
        ↓
[Atman Acharya Runtime]
        ↓
[User-facing Atman app]
        ↓
[Garuda Watch feedback]
        ↓
[NyayaBench + Corpus/Tune loops]
```

## 3. Runtime architecture

```text
User query
→ intent classifier
→ risk classifier
→ retrieval query expansion
→ BM25 + Qdrant + TattvaNet retrieval
→ reranking
→ source pack builder
→ Atman LLM adapter
→ citation renderer
→ answer contract validator
→ hallucination scorer
→ final answer
```

## 4. Agent architecture

```text
ShrutiKosh Corpus Agent
Atman Tune Agent
NyayaBench Verifier Agent
Atman Acharya Runtime Agent
Garuda Watch Monitor Agent
```

## 5. Storage architecture

| Store | Canonical use |
|---|---|
| PostgreSQL | sources, chunks, reviews, samples, model registry, release gates |
| Qdrant | dense vector retrieval |
| OpenSearch/PG trigram/BM25 | lexical retrieval |
| MinIO/S3 | PDFs, raw files, exports, checkpoints |
| Neo4j/Postgres graph | TattvaNet source/concept graph |
| JSONL | portable dataset/export format |
| Git | source code, canonical docs, migration history |

## 6. Deployment architecture

MVP:

```text
FastAPI + Postgres + Qdrant + MinIO + Redis + Next.js Studio + Next.js Web
```

Production:

```text
FastAPI service mesh
PostgreSQL HA
Qdrant cluster
Object storage
vLLM/SGLang/OpenAI-compatible serving
Worker queue
OpenTelemetry + Prometheus + Grafana
Auth/RBAC
Release gates
```

## 7. Non-negotiable invariant

```text
No public scripture answer without source retrieval or explicit uncertainty.
```

## 8. Trust boundary

| Boundary | Rule |
|---|---|
| User upload | untrusted until parsed, scanned, reviewed |
| OCR output | untrusted until quality score and review |
| LLM output | untrusted until contract + citation validation |
| Synthetic data | draft-only until human/reviewer approval |
| RAG index | production-valid only if built from approved Z2 chunks |
