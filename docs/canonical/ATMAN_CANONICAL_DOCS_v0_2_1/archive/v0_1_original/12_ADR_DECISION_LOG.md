# 12 — Architecture Decision Record Log

## ADR-001 — Atman is the master brand

**Decision:** Website and public brand are `Atman`.

**Rationale:** Short, spiritually aligned, usable for website/app/LLM.

## ADR-002 — AtmanOS is the backend platform

**Decision:** Use `AtmanOS` for the full system layer.

**Rationale:** Separates public brand from technical platform.

## ADR-003 — Atman LLM is the model family

**Decision:** Model family name is `Atman LLM`.

**Rationale:** User explicitly rejected alternative LLM names and locked Atman.

## ADR-004 — Use ShrutiKosh for corpus

**Decision:** Corpus system name is `ShrutiKosh`.

**Rationale:** Communicates knowledge/scripture vault without overclaiming.

## ADR-005 — Use TattvaNet for knowledge layer

**Decision:** Knowledge graph/network is `TattvaNet`.

**Rationale:** Better than DharmaJaal, which user rejected.

## ADR-006 — Use five core agents only

**Decision:** Keep top-level agent count capped at five.

**Rationale:** Prevent agent zoo; maintain lifecycle clarity.

## ADR-007 — Keep data zones loose before production

**Decision:** Z0/Z1 allow discovery/sandbox velocity; Z2 is strict.

**Rationale:** User requested less restrictive agents while preserving production safety.

## ADR-008 — Fine-tuning does not replace RAG

**Decision:** Fine-tuning is for behavior; RAG is for knowledge.

**Rationale:** Scripture/citation correctness requires retrieval and provenance.

## ADR-009 — Hindi-first runtime

**Decision:** Default response language is Hindi.

**Rationale:** User preference and target product identity.

## ADR-010 — Version folders during ChatGPT build

**Decision:** Continue generating separate folders/zips: `atman_v0_1`, `atman_v0_2`, etc.

**Rationale:** Safer snapshots in this build environment. Later migrate to one Git repo with tags.
