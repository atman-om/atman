# 03 — Agent Specifications

## 1. Agent stack

Atman uses 5 core agents. Subtasks should remain tools/submodules unless they own a separate lifecycle.

## 2. ShrutiKosh Corpus Agent

### Purpose

Create raw, draft, verified, and production-ready corpora.

### Inputs

- PDFs;
- scanned pages;
- plain text;
- web pages;
- teacher LLM output;
- user-authored notes;
- licensed/public-domain scripture.

### Submodules

```text
intake
pdf_parser
ocr_extractor
rights_classifier
zone_router
normalizer
chapter_verse_parser
chunker
ontology_tagger
teacher_generator
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

Judge generated data, runtime answers, and model checkpoints.

### Checks

```text
citation validity
faithfulness
fake shloka detection
source availability
Sanskrit consistency
sampradaya neutrality
unsafe ritual advice
copyright similarity
answer contract compliance
regression
```

## 5. Atman Acharya Runtime Agent

### Purpose

Answer users through a RAG + Atman LLM + validator pipeline.

### Duties

- classify query intent;
- retrieve sources;
- build source pack;
- generate answer;
- render citations;
- validate answer contract;
- refuse unsupported claims.

## 6. Garuda Watch Monitor Agent

### Purpose

Monitor production quality.

### Tracks

- bad answer reports;
- wrong citation reports;
- source not found;
- hallucination clusters;
- cost/latency;
- model regressions;
- feedback themes.

### Trigger logic

```text
Failure cluster
→ NyayaBench evaluation
→ Corpus fix or tuning dataset
→ Atman Tune Agent
→ release gate
```
