---
project: Atman
pack: ATMAN_CANONICAL_DOCS_v0_2
version: 0.2
status: execution-grade canonical baseline
created_at: 2026-05-28T13:00:36+05:30
timezone: Asia/Kolkata
canonical_rule: Any implementation, repo, model, dataset, or release gate must conform to this document pack or record an ADR.
---

# 21 — Model Training Runbook

## 1. Objective

Define the repeatable process for training, registering, evaluating, and promoting Atman LLM checkpoints.

## 2. Candidate base models

Base model selection must consider:

```text
Hindi quality
Sanskrit/tokenization support
license fit
context length
serving cost
fine-tuning ecosystem
safety behavior
```

Candidate families:

```text
Llama-family open models
Mistral-family open models
Qwen-family multilingual models
Indic-focused models when quality/licensing permits
```

A specific base model becomes canonical only after license review and NyayaBench baseline comparison.

## 3. Training stages

```text
dataset selection
→ rights validation
→ deduplication
→ formatting
→ train/dev/test split
→ baseline eval
→ LoRA/QLoRA run
→ checkpoint registration
→ NyayaBench eval
→ human review
→ release gate
```

## 4. Dataset format

```json
{
  "messages": [
    {"role": "system", "content": "..."},
    {"role": "user", "content": "..."},
    {"role": "assistant", "content": "..."}
  ],
  "metadata": {
    "source_chunk_ids": ["uuid"],
    "rights_status": "PUBLIC_DOMAIN_VERIFIED",
    "language": "hi",
    "sample_type": "retrieval_grounded"
  }
}
```

## 5. Canonical config

```yaml
method: qlora
precision: bf16
load_in_4bit: true
lora_rank: 64
lora_alpha: 128
lora_dropout: 0.05
learning_rate: 2.0e-5
num_train_epochs: 3
per_device_train_batch_size: 2
gradient_accumulation_steps: 16
context_length: 8192
optimizer: adamw_torch
scheduler: cosine
warmup_ratio: 0.03
gradient_checkpointing: true
save_steps: 500
eval_steps: 500
max_grad_norm: 1.0
```

## 6. Checkpoint registration

```json
{
  "model_name": "Atman-Hindi-8B",
  "version": "0.2.1-lora.1",
  "base_model": "...",
  "dataset_hash": "...",
  "training_config_hash": "...",
  "checkpoint_uri": "s3://...",
  "checkpoint_hash": "..."
}
```

## 7. Promotion policy

```text
trained → registered → evaluated → candidate → staging → production alias
```

Only a release gate may update `Atman-Prod`.

## 8. Abort criteria

Abort training/release if:

- dataset rights conflict;
- high duplicate leakage;
- eval loss diverges;
- fake shloka hard failures increase;
- citation faithfulness drops below threshold;
- safety regressions appear.
