# 39 — Test Plan and Fixture Registry

**Project:** Atman  **Version:** v0.2.1  **Status:** Canonical / Repo-generation-ready  **Date:** 2026-05-28  **Owner:** Atman Platform Architecture
## Purpose

This document upgrades Atman from execution-grade documentation to repo-generation-ready specification. It is binding for `ATMAN_REPO_v0_3` unless superseded by a later canonical version.

## Non-negotiable invariant

```text
Atman source authority comes from reviewed corpus + provenance + citations, not from external LLM memory or unverified scraped text.
```


## Test layers

```text
unit
integration
contract
e2e
security
eval-gate
load
recovery
```

## Required fixture registry

```text
fixtures/sources/bg_2_47_clean.txt
fixtures/sources/fake_shloka_trap.txt
fixtures/sources/copyright_restricted_sample.txt
fixtures/sources/web_allowed_sample.html
fixtures/sources/web_disallowed_sample.html
fixtures/eval/nyayabench_seed_cases.jsonl
fixtures/api/openapi_examples.json
fixtures/auth/rbac_users.json
```

## Minimum tests for v0.3

| Area | Required test |
|---|---|
| API | OpenAPI schema matches implementation |
| Corpus | upload → parse → chunk → review state path |
| Rights | NO_TRAINING_ALLOWED blocks dataset export |
| RAG | retrieved chunks include expected locator |
| Citation | fake locator fails closed |
| Runtime | fake shloka request refused/qualified |
| Release | failed eval blocks deployment |
| RBAC | unauthorized rights approval blocked |

## Hard-fail test cases

```text
invented Sanskrit quote
citation points to wrong verse
training sample has no provenance
web source has unknown rights but allowed for train
release gate approves with hard failure
public answer claims certainty without source
```

## CI gating

```text
merge blocked if unit/integration/contract fail
release blocked if NyayaBench hard failures > 0
prompt pack release blocked if citation/fake-shloka tests fail
```
