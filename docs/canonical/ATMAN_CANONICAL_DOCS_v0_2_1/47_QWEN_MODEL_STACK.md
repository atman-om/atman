# 47 — Qwen Model Stack

**Project:** Atman  **Version:** v0.2.1  **Status:** Canonical / Repo-generation-ready  **Date:** 2026-05-28  **Owner:** Atman Platform Architecture
## Purpose

This document upgrades Atman from execution-grade documentation to repo-generation-ready specification. It is binding for `ATMAN_REPO_v0_3` unless superseded by a later canonical version.

## Non-negotiable invariant

```text
Atman source authority comes from reviewed corpus + provenance + citations, not from external LLM memory or unverified scraped text.
```


## Canonical decision

```text
ATMAN_MODEL_BASE_FAMILY = Qwen
WORKING_MODEL_NAME = Atman-Lab-Qwen
PRODUCTION_MODEL_NAME = Atman-Prod only after release gate
```

## Model roles

| Role | Canonical candidate | Purpose |
|---|---|---|
| Dev/local | Atman-Dev-Qwen-8B-v0.1 | local testing, cheap pipeline debugging |
| Runtime/content | Atman-Lab-Qwen-14B-v0.1 | Ask Atman + content generation candidate |
| Research/high quality | Atman-Lab-Qwen-32B-v0.1 | deeper generation/review candidate |
| Verifier | Atman-Verifier-Qwen-4B-v0.1 | citation/safety/fake-shloka checks |
| Embedding | Atman-RAG-QwenEmbedding-v0.1 | dense retrieval |
| Reranker | Atman-RAG-QwenReranker-v0.1 | retrieval precision |

## Deployment profile

```text
v0.3 local: Qwen API/config placeholder + optional local 8B
v0.4 staging: Qwen 14B runtime candidate with RAG
v0.5 content factory: 14B/32B split by cost/quality
v1.0 prod: only model passing NyayaBench release gate
```

## Fine-tuning path

```text
1. Establish corpus + RAG first.
2. Build NyayaBench seed suite.
3. Run base Qwen against benchmarks.
4. Build reviewed instruction dataset.
5. Perform LoRA/QLoRA experiment.
6. Compare base vs LoRA vs RAG-only.
7. Promote only if quality increases without citation/fake-shloka regression.
```

## Initial LoRA configuration

```yaml
base_family: qwen
method: qlora
rank: 64
alpha: 128
dropout: 0.05
learning_rate: 0.00002
epochs: 3
context_length: 8192
optimizer: adamw
scheduler: cosine
```

## Hard gates

```text
fake shloka hard failures = 0
citation hard failures = 0
unsafe ritual hard failures = 0
rights/provenance hard failures = 0
Hindi quality score ≥ threshold
```

## Naming invariant

```text
Qwen is the base family.
Atman is the system: Qwen + Atman corpus + Atman RAG + Atman prompts + Atman guardrails + Atman evals + optional Atman LoRA.
```
