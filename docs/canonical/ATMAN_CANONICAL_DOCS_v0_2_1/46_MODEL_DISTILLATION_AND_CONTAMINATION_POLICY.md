# 46 — Model Distillation and Contamination Policy

**Project:** Atman  **Version:** v0.2.1  **Status:** Canonical / Repo-generation-ready  **Date:** 2026-05-28  **Owner:** Atman Platform Architecture
## Purpose

This document upgrades Atman from execution-grade documentation to repo-generation-ready specification. It is binding for `ATMAN_REPO_v0_3` unless superseded by a later canonical version.

## Non-negotiable invariant

```text
Atman source authority comes from reviewed corpus + provenance + citations, not from external LLM memory or unverified scraped text.
```


## Purpose

Protect Atman from illegal, low-quality, or terms-violating training contamination.

## Training data allowed

```text
public-domain verified corpus
licensed corpus with train permission
user-owned corpus with train permission
human-authored reviewed content
source-grounded synthetic data generated from allowed corpus
negative eval examples marked eval-only
```

## Training data blocked

```text
external LLM output where provider terms prohibit model development
copyrighted text without training permission
reference-only corpus
unknown-rights web scrape
unverified Sanskrit/scripture text
content with no source_ids/chunk_ids
```

## External LLM output rule

```text
External LLM output is draft assistance by default.
It can become training data only if:
1. provider terms allow it;
2. it is transformed into Atman-owned reviewed content;
3. it is source-aligned where factual;
4. it passes rights review;
5. provenance ledger records the assistance.
```

## Dataset export gate

```text
Export denied if any sample has:
rights_status not in allowlist
source_ids empty
review_status not APPROVED_FOR_TRAINING
external_llm_assisted=true and allowed_for_training=false
```

## Contamination audit

Run before every training job:

```text
sample provenance audit
rights matrix audit
eval/train leakage audit
copyright similarity audit
external-provider restriction audit
```
