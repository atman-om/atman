# CHANGELOG — v0.2 to v0.2.1

**Date:** 2026-05-28

## Added

- `31_OPENAPI_SPEC.md`
- `32_STATE_MACHINES.md`
- `33_RBAC_AND_ADMIN_PERMISSIONS.md`
- `34_SOURCE_LOCATOR_STANDARD.md`
- `35_PROMPT_PACK_SPEC.md`
- `36_SEED_DATASETS_AND_JSONL_FORMATS.md`
- `37_DOCKER_COMPOSE_AND_LOCAL_DEV.md`
- `38_UI_ROUTE_AND_COMPONENT_MAP.md`
- `39_TEST_PLAN_AND_FIXTURE_REGISTRY.md`
- `40_MODEL_SELECTION_DECISION_MATRIX.md`
- `41_WEB_TO_CORPUS_PIPELINE.md`
- `42_MULTI_LLM_EXTRACTION_POLICY.md`
- `43_CRAWLER_RIGHTS_AND_ROBOTS_POLICY.md`
- `44_WEB_SOURCE_QUALITY_SCORING.md`
- `45_CORPUS_PROVENANCE_LEDGER.md`
- `46_MODEL_DISTILLATION_AND_CONTAMINATION_POLICY.md`
- `47_QWEN_MODEL_STACK.md`

## Locked

```text
ATMAN_MODEL_BASE_FAMILY = Qwen
WORKING_MODEL_NAME = Atman-Lab-Qwen
External LLM output = draft/helper artifact only by default
Web corpus = rights/robots/provenance gated
```

## Added machine-readable assets

```text
schemas/*.json
schemas/openapi.yaml
prompts/*.md
datasets/eval/*.jsonl
infra/docker-compose.yml
infra/.env.example
migrations/001_initial_schema.sql
```

## Preserved

```text
archive/v0_1_original/
archive/v0_2_original/
```
