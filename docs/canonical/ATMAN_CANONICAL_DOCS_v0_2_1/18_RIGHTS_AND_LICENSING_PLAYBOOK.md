---
project: Atman
pack: ATMAN_CANONICAL_DOCS_v0_2
version: 0.2
status: execution-grade canonical baseline
created_at: 2026-05-28T13:00:36+05:30
timezone: Asia/Kolkata
canonical_rule: Any implementation, repo, model, dataset, or release gate must conform to this document pack or record an ADR.
---

# 18 — Rights and Licensing Playbook

## 1. Objective

Atman must separate discovery, internal experimentation, retrieval, quoting, and model training rights. No source is production-valid until rights are reviewed.

## 2. Rights states

```text
UNKNOWN
PUBLIC_DOMAIN_VERIFIED
LICENSED_VERIFIED
OPEN_LICENSE_VERIFIED
USER_OWNED
REFERENCE_ONLY
NO_TRAINING_ALLOWED
NO_STORAGE_ALLOWED
REJECTED
```

## 3. Allowed usage matrix

| Rights State | Store | Retrieve | Train | Quote | Public answer |
|---|---:|---:|---:|---:|---:|
| PUBLIC_DOMAIN_VERIFIED | ✅ | ✅ | ✅ | ✅ | ✅ |
| LICENSED_VERIFIED | ✅ | ✅ | depends | ✅ | depends |
| OPEN_LICENSE_VERIFIED | ✅ | ✅ | depends | ✅ | ✅ |
| USER_OWNED | ✅ | ✅ | ✅ | ✅ | ✅ |
| REFERENCE_ONLY | ✅ | ❌ | ❌ | limited | ❌ |
| NO_TRAINING_ALLOWED | ✅ | ✅ | ❌ | limited | depends |
| NO_STORAGE_ALLOWED | ❌ | ❌ | ❌ | ❌ | ❌ |
| REJECTED | ❌ | ❌ | ❌ | ❌ | ❌ |

## 4. Rights review record

```json
{
  "source_id": "uuid",
  "reviewer_id": "uuid",
  "rights_status": "PUBLIC_DOMAIN_VERIFIED",
  "evidence_uri": "s3://rights-evidence/...",
  "allowed_usage": {
    "store": true,
    "retrieve": true,
    "train": true,
    "quote": true,
    "public_answer": true
  },
  "jurisdiction_notes": "India/global public-domain check pending if uncertain",
  "reviewed_at": "..."
}
```

## 5. Red flags

- modern copyrighted commentary without license;
- scanned commercial books;
- unclear web scrape rights;
- content marked private/internal;
- translation copyright mismatch;
- unclear publisher/edition;
- user-uploaded material without ownership declaration.

## 6. Copyright similarity guard

Dataset exports and generated answers must be checked for near-verbatim reproduction when sources are not freely reproducible.

## 7. Review workflow

```text
source uploaded
→ draft classification
→ evidence collection
→ rights reviewer decision
→ allowed usage matrix stored
→ zone transition allowed/blocked
→ audit log created
```

## 8. Default rule

When rights are unknown, Atman may store only temporary metadata and internal triage notes. It must not train, publicly retrieve, or quote from the source.
