---
project: Atman
pack: ATMAN_CANONICAL_DOCS_v0_2
version: 0.2
status: execution-grade canonical baseline
created_at: 2026-05-28T13:00:36+05:30
timezone: Asia/Kolkata
canonical_rule: Any implementation, repo, model, dataset, or release gate must conform to this document pack or record an ADR.
---

# Changelog — v0.1 to v0.2

## Summary

v0.2 upgrades Atman from a canonical architecture pack into an execution-grade product/engineering baseline.

## Added documents

| Range | Added capability |
|---|---|
| `13` | PostgreSQL/Qdrant/Neo4j persistence schema |
| `14` | Monorepo and DevOps baseline |
| `15` | Agent tool contracts and state machines |
| `16` | TattvaNet ontology and tagging schema |
| `17` | NyayaBench datasets and grader mechanics |
| `18` | Rights/licensing workflow |
| `19` | Atman Studio admin UI |
| `20` | Public app UX |
| `21` | Model training runbook |
| `22` | Acceptance tests |
| `23` | Observability and telemetry |
| `24` | Synthetic data policy |
| `25` | Runtime safety guardrails |
| `26` | Search/index lifecycle |
| `27` | Artifact registry/versioning |
| `28` | Backup/recovery/retention |
| `29` | Environment variables/secrets |
| `30` | Operations runbook |

## Corrected invariants

- Synthetic generation may draft explanations, questions, and summaries, but it is never scripture authority.
- `Z2_PRODUCTION` now means rights-verified, source-verified, quality-reviewed, citation-addressable, and release-approved.
- All production scripture claims require source retrieval or explicit uncertainty.
- A model checkpoint is not production merely because training completed; it must pass a release gate.
- Agent autonomy is bounded by zone, rights, risk, and release-policy checks.
