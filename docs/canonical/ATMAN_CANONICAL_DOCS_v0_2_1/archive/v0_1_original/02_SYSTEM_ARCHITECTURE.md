# 02 — System Architecture

## 1. Architecture principle

Atman is a layered system:

```text
Corpus → Graph/RAG → Model behavior → Runtime verification → Monitoring loop
```

Knowledge must not live only inside model weights.

## 2. High-level architecture

```text
[Sources]
  ├─ PDFs/books
  ├─ web references
  ├─ public-domain texts
  ├─ licensed texts
  ├─ teacher LLM synthetic data
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
→ retrieval query expansion
→ Qdrant + TattvaNet source retrieval
→ source pack builder
→ Atman LLM adapter
→ citation renderer
→ answer contract validator
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
| PostgreSQL | sources, chunks, samples, model registry, release gates |
| Qdrant | vector retrieval |
| MinIO/S3 | PDFs, raw files, exports, checkpoints |
| Neo4j/Postgres graph | TattvaNet source/concept graph |
| JSONL | portable dataset/export format |
| Git | source code and versioned docs |

## 6. Deployment architecture

MVP:

```text
FastAPI + JSONL/Postgres + Qdrant + Next.js Studio + Next.js Web
```

Production:

```text
FastAPI services
PostgreSQL
Qdrant cluster
Object storage
vLLM/SGLang serving
Worker queue
Observability
Auth/RBAC
Release gates
```

## 7. Non-negotiable invariant

```text
No public scripture answer without source retrieval or explicit uncertainty.
```
