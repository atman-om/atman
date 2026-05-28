---
project: Atman
pack: ATMAN_CANONICAL_DOCS_v0_2
version: 0.2
status: execution-grade canonical baseline
created_at: 2026-05-28T13:00:36+05:30
timezone: Asia/Kolkata
canonical_rule: Any implementation, repo, model, dataset, or release gate must conform to this document pack or record an ADR.
---

# 03 — Agent Architecture

## 1. Agent stack

Atman uses 5 core agents. Subtasks remain tools/submodules unless they own a separate lifecycle.

```text
ShrutiKosh Corpus Agent
Atman Tune Agent
NyayaBench Verifier Agent
Atman Acharya Runtime Agent
Garuda Watch Monitor Agent
```

## 2. ShrutiKosh Corpus Agent

### Purpose

Create raw, draft, verified, and production-ready corpora.

### Inputs

- PDFs;
- scanned pages;
- plain text;
- web pages;
- teacher-model-assisted draft output;
- user-authored notes;
- licensed/public-domain scripture.

### Submodules

```text
intake
file_scanner
pdf_parser
ocr_extractor
rights_classifier
zone_router
normalizer
chapter_verse_parser
chunker
ontology_tagger
quality_scorer
dataset_exporter
```

### Outputs

```text
source_registry.jsonl
chunks.jsonl
rag_chunks.jsonl
sft_samples.jsonl
dpo_pairs.jsonl
eval_samples.jsonl
kg_triples.jsonl
```

## 3. Atman Tune Agent

### Purpose

Create Atman model variants from approved/draft data.

### Training tiers

| Tier | Data | Use |
|---|---|---|
| FT_LAB | Z1 allowed | internal |
| FT_STAGING | Z1 + reviewed Z2 | closed beta |
| FT_PROD | Z2 only | public |

### Supported methods

- SFT LoRA/QLoRA;
- DPO LoRA;
- later: full fine-tune;
- later: RFT only after reliable graders exist.

## 4. NyayaBench Verifier Agent

### Purpose

Judge whether datasets, RAG indexes, prompts, answers, and checkpoints are release-eligible.

### Hard-fail classes

```text
fake_shloka
missing_citation_for_scripture_claim
unsafe_ritual_procedure
rights_violation
sectarian_absolutism
copyright_reproduction
```

## 5. Atman Acharya Runtime Agent

### Purpose

Answer user questions with source-grounded, Hindi-first, policy-compliant output.

### Must use

```text
intent classifier
risk classifier
retriever
source-pack builder
LLM adapter
citation verifier
answer contract validator
feedback logger
```

## 6. Garuda Watch Monitor Agent

### Purpose

Detect drift, unsafe outputs, citation failures, low-rated clusters, and retraining triggers.

### Signals

```text
user feedback
answer reports
citation mismatch
latency spikes
cost spikes
retrieval misses
NyayaBench regression
```

## 7. Autonomy boundary

Agents may act automatically in Z0/Z1 for low-risk operations. Any movement into Z2, production release, or public answer behavior change requires review/gate approval.
