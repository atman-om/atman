# 40 — Model Selection Decision Matrix

**Project:** Atman  **Version:** v0.2.1  **Status:** Canonical / Repo-generation-ready  **Date:** 2026-05-28  **Owner:** Atman Platform Architecture
## Purpose

This document upgrades Atman from execution-grade documentation to repo-generation-ready specification. It is binding for `ATMAN_REPO_v0_3` unless superseded by a later canonical version.

## Non-negotiable invariant

```text
Atman source authority comes from reviewed corpus + provenance + citations, not from external LLM memory or unverified scraped text.
```


## Decision status

```text
Base family selected for lab: Qwen
Production model: not yet released
Canonical working name: Atman-Lab-Qwen
```

## Candidate roles

| Role | Primary candidate | Backup |
|---|---|---|
| Runtime/content | Qwen 14B | Qwen 32B / Mistral |
| Dev/local | Qwen 8B | Qwen 4B |
| Verifier | Qwen 4B / 1.7B | rules + classifier |
| Embedding | Qwen Embedding | BGE/E5 fallback |
| Reranking | Qwen Reranker | BGE reranker fallback |

## Scoring matrix

| Criterion | Weight | Hard fail? |
|---|---:|---:|
| Hindi generation quality | 15 | no |
| Sanskrit quote discipline | 15 | yes |
| Citation-following | 15 | yes |
| RAG obedience | 15 | yes |
| License/commercial deployability | 15 | yes |
| Serving cost | 10 | no |
| Context length | 5 | no |
| Tool/function calling | 5 | no |
| Quantization quality | 5 | no |

## Promotion rule

```text
Atman-Lab-Qwen may become Atman-Prod only if:
- total score ≥ 85/100
- fake shloka hard failures = 0
- citation hard failures = 0
- rights/provenance hard failures = 0
- release manager approval exists
```

## Model naming

```text
Atman-Dev-Qwen-8B-v0.1
Atman-Lab-Qwen-14B-v0.1
Atman-Lab-Qwen-32B-v0.1
Atman-Verifier-Qwen-4B-v0.1
Atman-RAG-QwenEmbedding-v0.1
Atman-RAG-QwenReranker-v0.1
Atman-Prod-v1.0
```

## Non-finalization rule

```text
Choosing Qwen means the lab base family is locked.
It does not mean a production model is released.
```
