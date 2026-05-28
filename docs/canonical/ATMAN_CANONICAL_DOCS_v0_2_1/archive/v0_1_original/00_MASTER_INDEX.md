# 00 — Atman Master Canonical Index

## 1. Executive definition

**Atman** is a Hindi-first Sanātan Dharma AI platform that combines source-governed corpus ingestion, scripture/commentary-aware retrieval, knowledge graph reasoning, fine-tuned model behavior, citation-backed runtime answering, evaluation gates, monitoring, and feedback loops.

Atman is not a generic chatbot. It is an **AI knowledge factory + user-facing assistant**.

## 2. Canonical architecture

```text
Sources
→ ShrutiKosh Corpus Agent
→ Z0/Z1/Z2 data zones
→ TattvaNet + RAG index
→ Atman LLM fine-tuning
→ NyayaBench evaluation
→ Atman Acharya runtime
→ Atman web app
→ Garuda Watch feedback
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
| ShrutiKosh | Corpus system | Ingest, clean, zone, chunk, tag sources |
| TattvaNet | Knowledge layer | Concepts, texts, traditions, source relationships |
| Atman LLM | Model family | Hindi/Sanskrit/Dharma assistant behavior |
| Atman Acharya | Runtime | User-facing answer engine |
| NyayaBench | Evaluation | Hallucination, citation, faithfulness, safety checks |
| Garuda Watch | Monitoring | Feedback, drift, rollback, retraining triggers |
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
| Z0_DISCOVERY | rough discovery, metadata, source hunting | no |
| Z1_SANDBOX | internal experiments, draft datasets, lab fine-tunes | no public use |
| Z2_PRODUCTION | owned/licensed/public-domain verified data | yes |

## 7. Canonical release logic

A model or corpus artifact can become production only if source provenance is known, rights status is GREEN or equivalent, citation validation passes, hallucination rate is below threshold, production answer contract passes, and release gate is approved.

## 8. Current repo progression

| Version | Canonical scope |
|---|---|
| v0.1 | FastAPI + source registry + local RAG scaffold |
| v0.2 | PDF upload/OCR/review/Qdrant scaffold |
| v0.3 | Qdrant runtime + Studio upload/review + SFT builder |
| v0.4 | LLM adapter + synthetic teacher pipeline + eval dashboard |
| v0.5 | TRL SFT/DPO training scaffold + checkpoint registry |
| v0.6 | licensing/quality/padaccheda/citation/contract validation |
| v0.7 | provenance/source graph/release gate/public web shell |
