# 42 — Multi-LLM Extraction Policy

**Project:** Atman  **Version:** v0.2.1  **Status:** Canonical / Repo-generation-ready  **Date:** 2026-05-28  **Owner:** Atman Platform Architecture
## Purpose

This document upgrades Atman from execution-grade documentation to repo-generation-ready specification. It is binding for `ATMAN_REPO_v0_3` unless superseded by a later canonical version.

## Non-negotiable invariant

```text
Atman source authority comes from reviewed corpus + provenance + citations, not from external LLM memory or unverified scraped text.
```


## Purpose

External LLMs may help Atman process sources, but they are not Atman’s epistemic authority.

## Allowed helper tasks

```text
OCR cleanup suggestions
chapter/section detection
claim extraction
concept tagging
summary draft
question generation draft
misconception generation draft
translation draft
format conversion
critique and review assistance
```

## Prohibited helper tasks

```text
generating scripture text from memory
generating citation locators without source spans
creating training samples with no provenance
washing copyrighted text through paraphrase
using provider outputs as direct competing-model training data where terms forbid it
```

## Multi-LLM verification pattern

```text
Source text
→ Extractor LLM creates structured draft
→ Verifier LLM checks alignment
→ deterministic validator checks locators/hashes
→ human review for high-risk items
→ approved artifact stored with provenance
```

## Storage rule

```text
Store helper output separately from reviewed corpus.
Never merge helper output into Z2 unless source-aligned and rights-approved.
```

## Contamination flags

```text
external_llm_assisted: true
provider: "openai|anthropic|google|local|other"
allowed_for_training: false by default
source_aligned: true|false
human_reviewed: true|false
```
