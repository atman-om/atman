---
project: Atman
pack: ATMAN_CANONICAL_DOCS_v0_2
version: 0.2
status: execution-grade canonical baseline
created_at: 2026-05-28T13:00:36+05:30
timezone: Asia/Kolkata
canonical_rule: Any implementation, repo, model, dataset, or release gate must conform to this document pack or record an ADR.
---

# 14 — Repo Structure and DevOps

## 1. Canonical monorepo

```text
atman/
├── apps/
│   ├── web/
│   ├── studio/
│   └── docs/
├── services/
│   ├── api/
│   ├── rag/
│   ├── inference/
│   ├── workers/
│   └── eval/
├── packages/
│   ├── schemas/
│   ├── ontology/
│   ├── corpus/
│   ├── telemetry/
│   └── prompts/
├── datasets/
│   ├── seed/
│   ├── synthetic/
│   ├── eval/
│   └── rejected/
├── infra/
│   ├── docker/
│   ├── kubernetes/
│   ├── terraform/
│   └── monitoring/
├── scripts/
├── tests/
└── canonical_docs/
```

## 2. Service responsibilities

| Service | Responsibility |
|---|---|
| `services/api` | REST API, auth, orchestration |
| `services/rag` | retrieval, reranking, source packs |
| `services/inference` | model gateway/adapters |
| `services/workers` | OCR, parsing, embedding, jobs |
| `services/eval` | NyayaBench execution |

## 3. Package responsibilities

| Package | Responsibility |
|---|---|
| `packages/schemas` | Pydantic/JSON schema/OpenAPI types |
| `packages/ontology` | entity/edge schema + TattvaNet utilities |
| `packages/corpus` | parsers, chunkers, normalizers |
| `packages/telemetry` | logging/tracing/metrics wrappers |
| `packages/prompts` | versioned prompt packs and tests |

## 4. Branching model

```text
main        = production-compatible
staging     = release candidate integration
dev         = active integration
feature/*   = isolated work
hotfix/*    = urgent production fixes
```

## 5. CI required stages

```text
format
lint
typecheck
unit_test
integration_test
migration_test
security_scan
container_scan
schema_compatibility_test
eval_smoke_gate
artifact_manifest_check
```

## 6. Release artifact manifest

Every release build must emit:

```json
{
  "release_version": "0.2.0",
  "git_sha": "...",
  "api_image": "...",
  "web_image": "...",
  "rag_index_version": "...",
  "model_alias": "...",
  "prompt_pack_version": "...",
  "migration_version": "..."
}
```

## 7. Local development command target

```text
make setup
make dev
make test
make eval-smoke
make build
make down
```

## 8. Non-negotiable dev rule

No engineer may bypass release gates by manually changing production aliases in the database or deployment environment.
