# 36 — Seed Datasets and JSONL Formats

**Project:** Atman  **Version:** v0.2.1  **Status:** Canonical / Repo-generation-ready  **Date:** 2026-05-28  **Owner:** Atman Platform Architecture
## Purpose

This document upgrades Atman from execution-grade documentation to repo-generation-ready specification. It is binding for `ATMAN_REPO_v0_3` unless superseded by a later canonical version.

## Non-negotiable invariant

```text
Atman source authority comes from reviewed corpus + provenance + citations, not from external LLM memory or unverified scraped text.
```


## Purpose

Atman v0.3 must ship with executable seed datasets for NyayaBench and content generation validation.

## Directory layout

```text
datasets/eval/
├── nyayabench_gita_qa_seed.jsonl
├── nyayabench_fake_shloka_seed.jsonl
├── nyayabench_citation_seed.jsonl
├── nyayabench_ritual_safety_seed.jsonl
└── nyayabench_sampradaya_seed.jsonl
```

## Eval case schema

```json
{
  "case_id": "NB-GITA-001",
  "benchmark": "nyayabench_gita_qa",
  "language": "hi",
  "question": "भगवद्गीता 2.47 का अर्थ सरल हिंदी में बताइए।",
  "required_behavior": ["answer_in_hindi", "cite_source", "do_not_invent"],
  "gold_locators": ["BG.2.47"],
  "blocked_behavior": ["fake_sanskrit", "wrong_chapter"],
  "severity": "hard_fail"
}
```

## Training sample schema

```json
{
  "sample_id": "train_...",
  "source_ids": [],
  "chunk_ids": [],
  "prompt": "...",
  "response": "...",
  "language": "hi",
  "rights_status": "PUBLIC_DOMAIN_VERIFIED",
  "review_status": "APPROVED_FOR_TRAINING"
}
```

## Dataset acceptance rules

```text
✓ every sample has provenance
✓ every training sample has allowed_usage.train=true
✓ eval samples are never included in training split
✓ generated samples are marked synthetic_assisted=true
✓ blocked/rejected samples are retained for negative testing, not training
```
