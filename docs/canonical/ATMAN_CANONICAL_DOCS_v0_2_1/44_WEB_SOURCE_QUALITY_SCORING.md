# 44 — Web Source Quality Scoring

**Project:** Atman  **Version:** v0.2.1  **Status:** Canonical / Repo-generation-ready  **Date:** 2026-05-28  **Owner:** Atman Platform Architecture
## Purpose

This document upgrades Atman from execution-grade documentation to repo-generation-ready specification. It is binding for `ATMAN_REPO_v0_3` unless superseded by a later canonical version.

## Non-negotiable invariant

```text
Atman source authority comes from reviewed corpus + provenance + citations, not from external LLM memory or unverified scraped text.
```


## Quality dimensions

| Dimension | Weight |
|---|---:|
| rights clarity | 25 |
| source authority | 20 |
| citation addressability | 20 |
| text extraction quality | 15 |
| duplication risk | 10 |
| doctrinal/context clarity | 10 |

## Score bands

```text
90–100: production candidate
75–89: sandbox/review
50–74: reference-only candidate
<50: reject unless manually overridden
```

## Hard-fail conditions

```text
pirated source suspected
no citation addressability for scripture claim
source text extraction corrupt beyond repair
license forbids storage/use
high copyright similarity with restricted source
```

## Score record

```json
{
  "source_id": "uuid",
  "quality_score": 87,
  "rights_clarity": 25,
  "source_authority": 17,
  "citation_addressability": 18,
  "extraction_quality": 14,
  "duplication_risk": 6,
  "context_clarity": 7,
  "hard_failures": []
}
```
