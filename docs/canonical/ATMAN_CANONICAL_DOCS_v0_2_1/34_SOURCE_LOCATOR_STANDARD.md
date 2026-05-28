# 34 — Source Locator Standard

**Project:** Atman  **Version:** v0.2.1  **Status:** Canonical / Repo-generation-ready  **Date:** 2026-05-28  **Owner:** Atman Platform Architecture
## Purpose

This document upgrades Atman from execution-grade documentation to repo-generation-ready specification. It is binding for `ATMAN_REPO_v0_3` unless superseded by a later canonical version.

## Non-negotiable invariant

```text
Atman source authority comes from reviewed corpus + provenance + citations, not from external LLM memory or unverified scraped text.
```


## Purpose

Atman citations must be deterministic, compact, human-readable, and machine-validated.

## Canonical locator grammar

```ebnf
locator = work "." location [":" edition] ["#" fragment]
work = UPPERCASE_TOKEN
location = segment { "." segment }
segment = UPPERCASE_TOKEN | integer
edition = UPPERCASE_TOKEN | year | publisher_token
fragment = "p" integer | "v" integer | "para" integer | "chunk" uuid
```

## Examples

```text
BG.2.47
BG.18.66:GITA_PRESS
COMMENTARY.SHANKARA.BG.2.47
COMMENTARY.RAMANUJA.BG.18.66
UPANISHAD.ISHA.1
RAMAYANA.BALAKANDA.1.1
MAHABHARATA.BHISHMA_PARVA.25.12
WEB.SRC_20260528_001#para3
BOOK.SRC_ABC123:p145
```

## Required citation fields

```json
{
  "locator": "BG.2.47",
  "work_id": "bg",
  "chapter": 2,
  "verse": 47,
  "edition_id": "critical_or_source_edition",
  "source_id": "uuid",
  "chunk_id": "uuid",
  "confidence": 0.99
}
```

## Work code registry

| Code | Work |
|---|---|
| `BG` | Bhagavad Gita |
| `UPANISHAD.ISHA` | Isha Upanishad |
| `RAMAYANA` | Ramayana |
| `MAHABHARATA` | Mahabharata |
| `PURANA.BHAGAVATA` | Bhagavata Purana |
| `COMMENTARY.SHANKARA` | Shankara commentary |
| `COMMENTARY.RAMANUJA` | Ramanuja commentary |
| `WEB` | reviewed web source |
| `BOOK` | source-book locator |

## Validation rules

```text
1. No citation displayed without source_id + chunk_id.
2. Locator must resolve to exactly one source span or fail closed.
3. Web locators must include retrieval date in source metadata.
4. Commentary locators must not be presented as base scripture.
5. Translation locators must include edition/translator metadata.
```

## Failure behavior

If locator validation fails:

```text
answer may still explain generally, but must say source citation is unavailable
scripture quote must be suppressed
release gate records ATMAN_CITATION_FAILED
```
