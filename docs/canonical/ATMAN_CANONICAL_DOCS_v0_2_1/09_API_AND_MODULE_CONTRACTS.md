---
project: Atman
pack: ATMAN_CANONICAL_DOCS_v0_2
version: 0.2
status: execution-grade canonical baseline
created_at: 2026-05-28T13:00:36+05:30
timezone: Asia/Kolkata
canonical_rule: Any implementation, repo, model, dataset, or release gate must conform to this document pack or record an ADR.
---

# 09 — API and Module Contracts

## 1. API standards

- All responses use JSON.
- All mutating requests require authenticated user context except public feedback when explicitly allowed.
- Every mutation creates an audit log.
- All list endpoints support pagination.
- All object IDs are UUIDs unless externally defined.

## 2. Core API groups

| Group | Endpoints |
|---|---|
| Health | `GET /health`, `GET /ready` |
| Sources | `POST /sources`, `GET /sources`, `GET /sources/{id}` |
| Uploads | `POST /uploads/pdf`, `GET /uploads/{id}/preview` |
| Review | `GET /review/sources`, `POST /review/sources/{id}/decision` |
| Ask | `POST /ask` |
| RAG | `POST /rag/debug`, `POST /index/rebuild` |
| Datasets | `POST /datasets/sft/build`, `POST /datasets/dpo/build`, `POST /datasets/export` |
| Training | `POST /training/runs`, `GET /training/checkpoints` |
| Eval | `POST /eval/run`, `GET /eval/runs/{id}` |
| Licensing | `GET /licensing/dashboard`, `POST /licensing/sources/{id}` |
| Corpus | `POST /corpus/deduplicate`, `GET /corpus/quality/chunks` |
| Sanskrit | `POST /sanskrit/padaccheda`, `POST /sanskrit/morphology` |
| Provenance | `GET /provenance/sources/{id}` |
| Release | `GET /release/gates`, `POST /release/gates/{id}/decision` |

## 3. Ask request

```json
{
  "question": "गीता 2.47 का अर्थ बताओ",
  "language": "hi",
  "mode": "simple",
  "require_citations": true
}
```

## 4. Ask response

```json
{
  "answer": "...",
  "citations": [
    {
      "source_id": "uuid",
      "chunk_id": "uuid",
      "title": "Bhagavad Gita 2.47",
      "work": "Bhagavad Gita",
      "chapter": "2",
      "verse": "47",
      "score": 0.91
    }
  ],
  "confidence": "high",
  "limitations": null,
  "contract": {
    "has_source_for_scripture_claim": true,
    "no_fake_shloka": true,
    "safe_uncertainty_if_needed": true
  }
}
```

## 5. Review decision request

```json
{
  "decision": "promote_z1_to_z2",
  "reason": "Public-domain source verified",
  "evidence_uri": "s3://...",
  "reviewer_notes": "..."
}
```

Allowed decisions:

```text
reject
needs_cleanup
promote_z0_to_z1
promote_z1_to_z2
mark_reference_only
mark_rights_red
deprecate
```

## 6. Error schema

```json
{
  "error": {
    "code": "RIGHTS_BLOCKED",
    "message": "Source rights do not allow this operation.",
    "details": {}
  },
  "request_id": "uuid"
}
```
