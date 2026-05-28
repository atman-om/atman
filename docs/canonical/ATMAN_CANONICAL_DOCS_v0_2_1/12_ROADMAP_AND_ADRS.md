---
project: Atman
pack: ATMAN_CANONICAL_DOCS_v0_2
version: 0.2
status: execution-grade canonical baseline
created_at: 2026-05-28T13:00:36+05:30
timezone: Asia/Kolkata
canonical_rule: Any implementation, repo, model, dataset, or release gate must conform to this document pack or record an ADR.
---

# 12 — Roadmap and ADRs

## 1. Version roadmap

| Version | Scope |
|---|---|
| v0.1 | canonical architecture baseline |
| v0.2 | execution-grade docs + ingestion implementation spec |
| v0.3 | review/retrieval implementation |
| v0.4 | LLM adapter + synthetic data/eval dashboard |
| v0.5 | fine-tuning execution + checkpoint registry |
| v0.6 | production readiness + licensing + Sanskrit modules |
| v0.7 | release gate + public web shell |
| v0.8 | auth + persistence + workflows |
| v0.9 | beta hardening |
| v1.0 | public MVP |

## 2. ADR log

### ADR-001 — Atman is the master brand

**Decision:** Website and public brand are `Atman`.

**Rationale:** Short, spiritually aligned, usable for website/app/LLM.

### ADR-002 — AtmanOS is the backend platform

**Decision:** Use `AtmanOS` for the full system layer.

**Rationale:** Separates public brand from technical platform.

### ADR-003 — Atman LLM is the model family

**Decision:** Model family name is `Atman LLM`.

**Rationale:** User explicitly rejected alternative LLM names and locked Atman.

### ADR-004 — Use ShrutiKosh for corpus

**Decision:** Corpus system name is `ShrutiKosh`.

**Rationale:** Communicates knowledge/scripture vault without overclaiming.

### ADR-005 — Use TattvaNet for knowledge layer

**Decision:** Knowledge graph/network is `TattvaNet`.

**Rationale:** Better than DharmaJaal, which user rejected.

### ADR-006 — Use five core agents only

**Decision:** Keep top-level agent count capped at five.

**Rationale:** Prevent agent zoo; maintain lifecycle clarity.

### ADR-007 — Keep data zones loose before production

**Decision:** Z0/Z1 allow discovery/sandbox velocity; Z2 is strict.

**Rationale:** Maintain research speed while protecting production safety.

### ADR-008 — Fine-tuning does not replace RAG

**Decision:** Fine-tuning is for behavior; RAG is for knowledge.

**Rationale:** Scripture/citation correctness requires retrieval and provenance.

### ADR-009 — Hindi-first runtime

**Decision:** Default response language is Hindi.

**Rationale:** User preference and target product identity.

### ADR-010 — Version folders during early build

**Decision:** Generate separate folders/zips for each version snapshot.

**Rationale:** Safer snapshots before migration to one Git repo with tags.

### ADR-011 — Synthetic data is non-authoritative

**Decision:** Synthetic data can teach format/explanation behavior but cannot be scripture or citation authority.

**Rationale:** Prevent hallucinated religious text from entering production.
