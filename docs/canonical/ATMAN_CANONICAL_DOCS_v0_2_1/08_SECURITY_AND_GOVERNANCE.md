---
project: Atman
pack: ATMAN_CANONICAL_DOCS_v0_2
version: 0.2
status: execution-grade canonical baseline
created_at: 2026-05-28T13:00:36+05:30
timezone: Asia/Kolkata
canonical_rule: Any implementation, repo, model, dataset, or release gate must conform to this document pack or record an ADR.
---

# 08 — Security and Governance

## 1. Governance objective

Atman must protect source integrity, user trust, rights compliance, reviewer accountability, and release safety.

## 2. Governance objects

| Object | Governance requirement |
|---|---|
| Source | rights review + provenance + checksum |
| Chunk | citation locator + quality score + review state |
| Dataset | source lineage + intended use + export hash |
| Model checkpoint | training config + dataset hash + eval result |
| RAG index | input chunk snapshot + embedding model + release gate |
| Prompt pack | versioned + test coverage + rollback path |
| Release | approvals + metrics + immutable record |

## 3. RBAC roles

| Role | Capabilities |
|---|---|
| Viewer | read dashboards |
| Corpus Editor | upload/parse/chunk sources |
| Rights Reviewer | approve rights states |
| Quality Reviewer | approve chunks and tags |
| Eval Reviewer | run and approve benchmarks |
| Release Manager | approve deployment gates |
| Admin | manage users, secrets, system settings |

## 4. Audit log events

```text
source_uploaded
rights_decision_changed
chunk_promoted
index_built
dataset_exported
training_started
checkpoint_registered
eval_run_completed
release_gate_decision
runtime_policy_changed
incident_opened
rollback_executed
```

## 5. Security controls

- Studio requires auth;
- RBAC enforced server-side;
- uploaded files scanned;
- source checksums recorded;
- secrets never committed;
- public ask endpoint rate-limited;
- model output logged with privacy redaction;
- release gate approval before production deployment.

## 6. Privacy baseline

User queries may be logged for quality only when policy allows. Logs must support redaction and deletion.
