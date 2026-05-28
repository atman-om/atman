# 43 — Crawler Rights and Robots Policy

**Project:** Atman  **Version:** v0.2.1  **Status:** Canonical / Repo-generation-ready  **Date:** 2026-05-28  **Owner:** Atman Platform Architecture
## Purpose

This document upgrades Atman from execution-grade documentation to repo-generation-ready specification. It is binding for `ATMAN_REPO_v0_3` unless superseded by a later canonical version.

## Non-negotiable invariant

```text
Atman source authority comes from reviewed corpus + provenance + citations, not from external LLM memory or unverified scraped text.
```


## Purpose

Atman crawler behavior must be conservative, auditable, and reversible.

## Crawler identity

```text
User-Agent: AtmanBot/0.1 (+contact URL after public launch)
```

## Pre-crawl checks

```text
robots.txt
terms-of-service classification
license marker detection
paywall/login detection
rate-limit policy
source category risk score
```

## Crawl policy

| Signal | Action |
|---|---|
| robots disallow | do not crawl |
| ToS disallow | do not crawl |
| paywall/login required | do not crawl unless licensed |
| open license detected | crawl to review |
| public domain verified | crawl to review |
| unknown rights | crawl metadata only or reference-only sandbox |

## Rate limit defaults

```text
max 1 request/sec/domain
respect crawl-delay if present
max depth 2 by default
max pages/domain/job configurable
```

## Removal / revocation

If a source requests removal or rights status changes:

```text
1. mark source as REVOKED
2. remove from production RAG index
3. block training export
4. preserve audit ledger unless legally required to delete
5. trigger answer/content revalidation for affected artifacts
```
