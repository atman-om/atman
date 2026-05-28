# 00 — Master Index

**Project:** Atman  **Version:** v0.2.1  **Status:** Canonical / Repo-generation-ready  **Date:** 2026-05-28  **Owner:** Atman Platform Architecture
## Purpose

This document upgrades Atman from execution-grade documentation to repo-generation-ready specification. It is binding for `ATMAN_REPO_v0_3` unless superseded by a later canonical version.

## Non-negotiable invariant

```text
Atman source authority comes from reviewed corpus + provenance + citations, not from external LLM memory or unverified scraped text.
```


## Package contents

This v0.2.1 package preserves all v0.2 root documents, the original v0.1 archive, and adds repo-generation-ready execution specs plus machine-readable assets.

## Canonical document list

| Range | Meaning |
|---|---|
| 00–12 | original architecture, agents, RAG, tuning, governance, roadmap |
| 13–30 | execution-grade platform specs from v0.2 |
| 31–47 | repo-generation-ready patch specs from v0.2.1 |

## New v0.2.1 docs

```text
31_OPENAPI_SPEC.md
32_STATE_MACHINES.md
33_RBAC_AND_ADMIN_PERMISSIONS.md
34_SOURCE_LOCATOR_STANDARD.md
35_PROMPT_PACK_SPEC.md
36_SEED_DATASETS_AND_JSONL_FORMATS.md
37_DOCKER_COMPOSE_AND_LOCAL_DEV.md
38_UI_ROUTE_AND_COMPONENT_MAP.md
39_TEST_PLAN_AND_FIXTURE_REGISTRY.md
40_MODEL_SELECTION_DECISION_MATRIX.md
41_WEB_TO_CORPUS_PIPELINE.md
42_MULTI_LLM_EXTRACTION_POLICY.md
43_CRAWLER_RIGHTS_AND_ROBOTS_POLICY.md
44_WEB_SOURCE_QUALITY_SCORING.md
45_CORPUS_PROVENANCE_LEDGER.md
46_MODEL_DISTILLATION_AND_CONTAMINATION_POLICY.md
47_QWEN_MODEL_STACK.md
```

## Machine-readable assets

```text
schemas/openapi.yaml
schemas/source.schema.json
schemas/chunk.schema.json
schemas/eval_case.schema.json
schemas/release_gate.schema.json
schemas/rights_review.schema.json
prompts/*.md
datasets/eval/*.jsonl
infra/docker-compose.yml
infra/.env.example
migrations/001_initial_schema.sql
fixtures/README.md
```

## Locked decisions

```text
Base model family for lab: Qwen
Production model: not released yet
Web-to-corpus: allowed only through rights/robots/provenance pipeline
External LLMs: helper workers only, never source authority
Atman Prod release: blocked unless NyayaBench hard failures are zero
```
