---
project: Atman
pack: ATMAN_CANONICAL_DOCS_v0_2
version: 0.2
status: execution-grade canonical baseline
created_at: 2026-05-28T13:00:36+05:30
timezone: Asia/Kolkata
canonical_rule: Any implementation, repo, model, dataset, or release gate must conform to this document pack or record an ADR.
---

# 00 — Atman Master Canonical Index

## 1. Executive definition

**Atman** is a Hindi-first Sanātan Dharma AI platform that combines source-governed corpus ingestion, scripture/commentary-aware retrieval, ontology-backed concept reasoning, fine-tuned model behavior, citation-backed answering, benchmark gates, monitoring, and feedback loops.

Atman is not a generic chatbot. It is an **AI knowledge factory + source-governed public assistant**.

## 2. Canonical architecture

```text
Sources
→ ShrutiKosh Corpus Agent
→ Z0/Z1/Z2 data zones
→ TattvaNet ontology + RAG index
→ Atman LLM behavior-tuned model family
→ NyayaBench evaluation
→ Atman Acharya runtime
→ Atman web app
→ Garuda Watch feedback loop
```

## 3. Core invariant

```text
Fine-tuning improves behavior.
RAG provides source-grounded knowledge.
NyayaBench decides release eligibility.
Garuda Watch closes the feedback loop.
```

## 4. Canonical components

| Component | Type | Purpose |
|---|---|---|
| Atman | Brand/product | Public website/app |
| AtmanOS | Platform | Backend intelligence system |
| ShrutiKosh | Corpus system | Ingest, clean, zone, chunk, tag, review, and export sources |
| TattvaNet | Knowledge layer | Concepts, texts, traditions, citations, commentarial relationships |
| Atman LLM | Model family | Hindi/Sanskrit/Dharma answer behavior |
| Atman Acharya | Runtime | User-facing answer engine |
| NyayaBench | Evaluation | Hallucination, citation, faithfulness, source, and safety checks |
| Garuda Watch | Monitoring | Feedback, drift, incidents, rollback, retraining triggers |
| Atman Studio | Admin UI | Corpus review, evals, model registry, release gates |

## 5. Model family

```text
Atman-Lab-8B
Atman-Hindi-8B
Atman-Sanskrit-8B
Atman-Acharya-14B
Atman-Scholar-32B
Atman-Guard-8B
Atman-Prod
```

## 6. Data zones

| Zone | Purpose | Production use |
|---|---|---|
| Z0_DISCOVERY | rough discovery, metadata, source hunting, rights triage | no |
| Z1_SANDBOX | internal experiments, draft datasets, lab fine-tunes | no public use |
| Z2_PRODUCTION | rights-verified + source-verified + quality-reviewed + citation-addressable + release-approved data | yes |

## 7. Canonical release logic

A model, corpus, RAG index, prompt pack, ontology, or runtime artifact can become production only if:

- source provenance is known;
- rights status allows intended use;
- citation validation passes;
- hallucination rate remains below threshold;
- fake Sanskrit/shloka traps pass;
- unsafe ritual/procedure behavior is zero-tolerance clean;
- production answer contract passes;
- release gate is approved and signed.

## 8. v0.2 document map

| Doc | Scope |
|---|---|
| `00` | Master index |
| `01` | Vision/principles |
| `02` | System architecture |
| `03` | Agent architecture |
| `04` | Corpus/data zones |
| `05` | RAG/retrieval |
| `06` | Fine-tuning/model strategy |
| `07` | Runtime behavior |
| `08` | Security/governance |
| `09` | API/module contracts |
| `10` | Infrastructure/deployment |
| `11` | Evaluation/release gates |
| `12` | Roadmap/ADRs |
| `13–30` | Execution specs required before repo implementation |

## 9. Repository progression

| Version | Canonical scope |
|---|---|
| v0.1 | FastAPI + source registry + local RAG scaffold |
| v0.2 | PDF upload/OCR/review/Qdrant scaffold + execution docs |
| v0.3 | Qdrant runtime + Studio upload/review + SFT builder |
| v0.4 | LLM adapter + synthetic teacher pipeline + eval dashboard |
| v0.5 | TRL SFT/DPO training scaffold + checkpoint registry |
| v0.6 | licensing/quality/padaccheda/citation/contract validation |
| v0.7 | provenance/source graph/release gate/public web shell |
