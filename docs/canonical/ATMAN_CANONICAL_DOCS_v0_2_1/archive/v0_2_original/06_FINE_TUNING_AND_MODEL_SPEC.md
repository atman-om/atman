---
project: Atman
pack: ATMAN_CANONICAL_DOCS_v0_2
version: 0.2
status: execution-grade canonical baseline
created_at: 2026-05-28T13:00:36+05:30
timezone: Asia/Kolkata
canonical_rule: Any implementation, repo, model, dataset, or release gate must conform to this document pack or record an ADR.
---

# 06 — Fine-Tuning and Model Specification

## 1. Principle

Fine-tuning improves behavior, format, language fluency, refusal discipline, pedagogy, and source-use habits. It does not replace RAG.

## 2. Model roles

| Model | Use |
|---|---|
| Atman-Lab-8B | internal experiments |
| Atman-Hindi-8B | Hindi-first assistant behavior |
| Atman-Sanskrit-8B | Sanskrit-aware support behavior |
| Atman-Acharya-14B | production answer candidate |
| Atman-Scholar-32B | advanced comparative mode |
| Atman-Guard-8B | policy/contract validation |
| Atman-Prod | currently approved production alias |

## 3. Dataset classes

| Dataset | Allowed source |
|---|---|
| human_verified | Z2 + reviewer-approved |
| retrieval_grounded | Z2 source packs |
| synthetic_teacher_draft | Z1 only unless reviewed |
| adversarial | generated/evaluated traps |
| refusal_policy | safe uncertainty examples |
| style_hindi | Hindi explanation formatting |

## 4. Training tiers

| Tier | Data | Release eligibility |
|---|---|---|
| FT_LAB | Z1/Z2 | no public release |
| FT_STAGING | reviewed Z1 + Z2 | closed beta only |
| FT_PROD | Z2 + approved synthetic explanatory samples | public candidate |

## 5. Canonical LoRA config

```yaml
method: qlora
lora_rank: 64
lora_alpha: 128
lora_dropout: 0.05
learning_rate: 2.0e-5
epochs: 3
context_length: 8192
optimizer: adamw_torch
scheduler: cosine
warmup_ratio: 0.03
gradient_checkpointing: true
save_strategy: steps
eval_strategy: steps
```

## 6. Dataset mixture baseline

| Dataset | Weight |
|---|---:|
| human_verified | 50% |
| retrieval_grounded | 30% |
| synthetic_teacher_draft_reviewed | 15% |
| adversarial/refusal | 5% |

## 7. Production ban

A checkpoint is not production because it trained successfully. It becomes production only after:

```text
checkpoint_registered
NyayaBench_passed
safety_gate_passed
citation_gate_passed
release_approved
alias_promoted_to_Atman-Prod
```
