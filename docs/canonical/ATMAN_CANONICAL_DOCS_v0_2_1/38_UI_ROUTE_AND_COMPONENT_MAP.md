# 38 — UI Route and Component Map

**Project:** Atman  **Version:** v0.2.1  **Status:** Canonical / Repo-generation-ready  **Date:** 2026-05-28  **Owner:** Atman Platform Architecture
## Purpose

This document upgrades Atman from execution-grade documentation to repo-generation-ready specification. It is binding for `ATMAN_REPO_v0_3` unless superseded by a later canonical version.

## Non-negotiable invariant

```text
Atman source authority comes from reviewed corpus + provenance + citations, not from external LLM memory or unverified scraped text.
```


## Atman Studio routes

```text
/studio
/studio/sources
/studio/sources/new
/studio/sources/:id
/studio/sources/:id/ocr
/studio/sources/:id/chunks
/studio/sources/:id/rights
/studio/ontology
/studio/rag-debugger
/studio/content-factory
/studio/content-review
/studio/evals
/studio/models
/studio/release-gates
/studio/audit-logs
/studio/settings/users
```

## Public app routes

```text
/
/ask
/shloka
/learn/gita
/concepts/:slug
/sources
/sources/:source_id
/account/saved
/feedback
```

## Studio component map

| Route | Core components |
|---|---|
| `/studio/sources` | SourceTable, SourceFilters, StateBadge |
| `/studio/sources/:id/ocr` | OCRPane, TextDiffViewer, SaveCorrectionButton |
| `/studio/sources/:id/rights` | RightsMatrix, EvidenceUploader, DecisionPanel |
| `/studio/rag-debugger` | QueryBox, RetrievalList, RerankTrace, CitationMap |
| `/studio/content-factory` | TemplateSelector, SourcePackPicker, BatchJobPanel |
| `/studio/evals` | BenchmarkSelector, EvalRunTable, FailureInspector |
| `/studio/release-gates` | GateSummary, MetricCards, ApprovalPanel, RollbackPanel |

## Required page states

```text
loading
empty
permission_denied
validation_error
network_error
success
conflict_state_transition
```

## UX invariants

```text
1. Review screens must show provenance.
2. Approve buttons are disabled if required checks fail.
3. Dangerous actions require reason text.
4. Release gate screen must show hard failures above soft warnings.
5. Public answer screen must show citations or explicit no-citation notice.
```
