---
project: Atman
pack: ATMAN_CANONICAL_DOCS_v0_2
version: 0.2
status: execution-grade canonical baseline
created_at: 2026-05-28T13:00:36+05:30
timezone: Asia/Kolkata
canonical_rule: Any implementation, repo, model, dataset, or release gate must conform to this document pack or record an ADR.
---

# 19 — Atman Studio UI Specification

## 1. Objective

Atman Studio is the internal admin dashboard for corpus ingestion, rights review, chunk QA, ontology tagging, dataset building, evaluation, and release approval.

## 2. Required screens

```text
Dashboard
Source Upload
OCR Review
Rights Review
Chunk Review
Ontology Editor
RAG Debugger
Dataset Builder
Training Runs
Benchmark Viewer
Checkpoint Registry
Release Gates
Feedback Inbox
Audit Logs
Settings
```

## 3. Dashboard

Must show:

- source counts by zone;
- rights queue counts;
- failed OCR/review counts;
- latest eval failures;
- active incidents;
- current production model/RAG index;
- pending release gates.

## 4. Source Upload

Fields:

```text
title
source type
language
script
tradition scope
file/url
claimed rights status
uploader notes
```

Actions:

```text
upload
scan
parse
send to rights review
```

## 5. OCR Review

Must show:

```text
page image
OCR text
confidence score
manual correction editor
page-level approval
```

## 6. Rights Review

Must show:

```text
source metadata
file preview
existing rights status
evidence upload/link
allowed usage matrix
decision buttons
reviewer notes
```

## 7. Chunk Review

Must show:

```text
chunk text
source locator
quality score
duplicate warning
rights status
approval/reject buttons
```

## 8. Ontology Editor

Must support:

```text
entity search
entity merge
alias edit
edge review
evidence chunk binding
tradition scope tagging
```

## 9. RAG Debugger

Must show:

```text
query
normalized query
retrieved chunks
BM25 score
dense score
rerank score
selected source pack
answer draft
citation validation result
hallucination score
```

## 10. Benchmark Viewer

Must show:

```text
eval run list
benchmark version
pass/fail summary
hard failures
case-level drilldown
regression comparison
```

## 11. Release Gates

Must show:

```text
artifact type
artifact version
metrics
hard failures
required approvals
approve/reject buttons
rollback target
```

## 12. RBAC visibility

Users must see only actions permitted by role. UI hiding is not enough; server-side enforcement is mandatory.
