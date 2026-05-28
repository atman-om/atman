# 35 — Prompt Pack Specification

**Project:** Atman  **Version:** v0.2.1  **Status:** Canonical / Repo-generation-ready  **Date:** 2026-05-28  **Owner:** Atman Platform Architecture
## Purpose

This document upgrades Atman from execution-grade documentation to repo-generation-ready specification. It is binding for `ATMAN_REPO_v0_3` unless superseded by a later canonical version.

## Non-negotiable invariant

```text
Atman source authority comes from reviewed corpus + provenance + citations, not from external LLM memory or unverified scraped text.
```


## Purpose

Prompt files are versioned runtime artifacts. They must be stored, checksummed, tested, and release-gated like code.

## Prompt pack layout

```text
prompts/
├── system_atman_acharya_hi.md
├── rag_answer_prompt_hi.md
├── citation_validator_prompt.md
├── fake_shloka_detector_prompt.md
├── safety_guard_prompt.md
├── extractor_claims_prompt.md
├── rights_classifier_prompt.md
└── content_factory_prompt_hi.md
```

## Prompt metadata block

Every prompt file must begin with:

```yaml
---
prompt_id: system_atman_acharya_hi
version: v0.2.1
language: hi
type: system
owner: runtime
hard_invariants:
  - no_fake_shloka
  - source_grounded_answering
  - uncertainty_over_hallucination
---
```

## Prompt release rules

```text
1. Prompt changes require eval run.
2. Prompt pack cannot release if fake-shloka cases fail.
3. Runtime prompt and citation validator prompt are coupled artifacts.
4. Prompt checksums are stored in artifact registry.
```

## Runtime prompt stack

```text
system_atman_acharya_hi
+ safety_guard_prompt
+ rag_answer_prompt_hi
+ source citation pack
+ user query
```

## Content generation prompt stack

```text
system_atman_acharya_hi
+ content_factory_prompt_hi
+ template specification
+ approved source pack
+ generation constraints
```

## Forbidden prompt behavior

```text
never ask the model to invent Sanskrit
never ask the model to complete missing verses from memory
never ask the model to cite without source pack
never ask external LLMs to become source authority
```
