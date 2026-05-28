# Model Lab Parallel Fine-Tuning Runbook

## Goal

Run Qwen adaptation experiments without blocking the live Atman product.

## Data allowed

Allowed:

- verified canonical corpus-derived Q&A
- reviewed generated content
- reviewer-corrected bad answers
- adversarial failure cases

Blocked:

- raw scraped data
- quarantine-only material
- unverified Sanskrit
- external LLM output without source-grounding and review

## Flow

```text
chat feedback + reviewed content + canonical passages
→ dataset plan
→ simulated LoRA/QLoRA run
→ checkpoint registry
→ NyayaBench gate
→ staging candidate
→ production only if strictly better and safer
```

## Primary APIs

```text
GET  /model-lab/readiness
POST /model-lab/dataset-plan
POST /model-lab/experiments
GET  /model-lab/comparison
```
