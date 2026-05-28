---
project: Atman
pack: ATMAN_CANONICAL_DOCS_v0_2
version: 0.2
status: execution-grade canonical baseline
created_at: 2026-05-28T13:00:36+05:30
timezone: Asia/Kolkata
canonical_rule: Any implementation, repo, model, dataset, or release gate must conform to this document pack or record an ADR.
---

# Atman Canonical Docs v0.2

## Pack purpose

This zip contains the complete **Atman execution-grade canonical documentation pack**. It includes:

1. upgraded v0.2 canonical docs `00–30` at the root;
2. the original v0.1 docs preserved under `archive/v0_1_original/`;
3. a machine-readable `manifest.json`;
4. a migration note from v0.1 to v0.2.

## Canonical naming

| Layer | Canonical name |
|---|---|
| Website / public brand | Atman |
| Core platform | AtmanOS |
| LLM family | Atman LLM |
| Corpus system | ShrutiKosh |
| Knowledge layer | TattvaNet |
| Runtime assistant | Atman Acharya |
| Evaluator | NyayaBench |
| Monitor | Garuda Watch |
| Admin dashboard | Atman Studio |

## v0.2 rule

v0.1 described the architecture. v0.2 governs execution.

Every artifact must be:

```text
traceable
schema-bound
reviewable
versioned
benchmarkable
reversible
release-gated
```

## Physical layout

```text
ATMAN_CANONICAL_DOCS_v0_2/
├── README.md
├── 00_MASTER_INDEX.md
├── ...
├── 30_OPERATIONS_RUNBOOK.md
├── CHANGELOG_v0_1_to_v0_2.md
├── manifest.json
└── archive/
    └── v0_1_original/
```

## Non-negotiable invariant

```text
Fine-tuning improves behavior.
RAG provides source-grounded knowledge.
NyayaBench decides release eligibility.
Garuda Watch closes the feedback loop.
```
