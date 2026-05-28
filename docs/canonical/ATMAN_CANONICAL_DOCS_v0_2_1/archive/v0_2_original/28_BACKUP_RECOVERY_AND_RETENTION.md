---
project: Atman
pack: ATMAN_CANONICAL_DOCS_v0_2
version: 0.2
status: execution-grade canonical baseline
created_at: 2026-05-28T13:00:36+05:30
timezone: Asia/Kolkata
canonical_rule: Any implementation, repo, model, dataset, or release gate must conform to this document pack or record an ADR.
---

# 28 — Backup, Recovery, and Retention

## 1. Objective

Protect Atman against data loss, corruption, accidental deletion, rights revocation mistakes, and bad releases.

## 2. Backup classes

| Class | Backup target |
|---|---|
| Metadata | PostgreSQL |
| Vector index | Qdrant snapshots |
| Corpus files | S3/MinIO object backup |
| Checkpoints | model storage bucket |
| Eval results | PostgreSQL + artifacts |
| Canonical docs | Git + zip snapshots |

## 3. Recovery targets

| Target | RTO |
|---|---:|
| API service | < 15 min |
| PostgreSQL metadata | < 30 min |
| Corpus object storage | < 1 hr |
| Ontology graph | < 1 hr |
| Vector DB | < 2 hr |
| Model serving | < 30 min |

## 4. Retention baseline

| Artifact | Retention |
|---|---|
| audit logs | 7 years or legal requirement |
| source rights evidence | lifetime of source + 7 years |
| raw uploaded files | per rights/storage policy |
| deprecated indexes | minimum rollback window |
| model checkpoints | until successor stable + retention window |
| user feedback | per privacy policy |

## 5. Restore drill

A restore drill must verify:

```text
Postgres restore
object restore
Qdrant restore
release alias restore
API starts against restored state
sample /ask works
```

## 6. Deletion and rights revocation

If a source becomes disallowed:

```text
mark source revoked
remove chunks from candidate/production indexes
invalidate dependent datasets where required
flag dependent model checkpoints
open release review
preserve audit evidence
```

## 7. Corruption handling

If citation corruption or index mismatch is detected, production RAG index must be rolled back to previous approved snapshot.
