# 11 — Version Roadmap

## v0.1 — Foundation

- FastAPI backend
- source registry
- Z0/Z1/Z2 zones
- local JSONL storage
- local RAG-style retriever
- NyayaBench Lite
- seed Gita sample

## v0.2 — Ingestion

- PDF upload
- OCR/text extraction
- chapter/verse parser
- source review API
- Qdrant vector index scaffold
- Atman Studio scaffold

## v0.3 — Review + Retrieval

- Qdrant-backed runtime retrieval
- Studio upload/review UI
- PDF preview metadata
- OCR quality scoring
- source-to-chunk drilldown
- SFT dataset builder

## v0.4 — LLM + Synthetic Data

- LLM runtime adapter
- teacher synthetic pipeline
- LoRA/QLoRA scaffold
- eval dashboard
- answer feedback loop
- RAG debugger UI

## v0.5 — Fine-Tuning Execution

- HuggingFace JSONL loader
- executable TRL SFTTrainer path
- DPO dataset builder
- DPO training scaffold
- checkpoint registry
- model comparison dashboard
- answer replay harness

## v0.6 — Production Readiness

- licensing dashboard
- corpus deduplication
- semantic chunk quality scoring
- multilingual Hindi/Sanskrit normalization
- padaccheda schema
- citation renderer
- answer contract validator

## v0.7 — Release Gate

- source graph
- provenance ledger
- Sanskrit morphology adapter interface
- citation-backed runtime renderer
- /ask contract validation
- production release gate
- user-facing web shell

## v0.8 — Auth + Persistence

Planned:

- auth + roles;
- workspace/project isolation;
- real Postgres persistence;
- Qdrant production collection manager;
- source graph visualization;
- provenance timeline UI;
- release-gate approval workflow;
- public answer feedback widget.

## v0.9 — Beta Hardening

Planned:

- full Atman Studio workflows;
- reviewer assignment queues;
- beta user management;
- model A/B testing;
- cost and latency dashboard;
- source pack reranker;
- improved Sanskrit morphology provider.

## v1.0 — Public MVP

Target:

- Bhagavad Gita Hindi-first source-backed assistant;
- public Atman web app;
- Studio production workflow;
- release gate;
- model registry;
- citation-backed answers;
- feedback loop;
- initial Atman-Lab/Atman-Hindi model path.
