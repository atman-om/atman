---
project: Atman
pack: ATMAN_CANONICAL_DOCS_v0_2
version: 0.2
status: execution-grade canonical baseline
created_at: 2026-05-28T13:00:36+05:30
timezone: Asia/Kolkata
canonical_rule: Any implementation, repo, model, dataset, or release gate must conform to this document pack or record an ADR.
---

# 24 — Synthetic Data Policy

## 1. Hard invariant

```text
Synthetic data is never scripture authority.
```

## 2. Allowed synthetic types

```text
summaries
qa_pairs
misconceptions
explanations
teaching styles
difficulty scaling
comparisons
refusal examples
adversarial traps
format examples
```

## 3. Forbidden synthetic types

```text
invented shlokas
invented Sanskrit
fake citations
fabricated commentary
invented historical claims
fabricated guru lineage
fabricated ritual procedures
```

## 4. Labeling requirement

Every synthetic sample must include:

```json
{
  "sample_type": "synthetic_teacher_draft",
  "generator_model": "...",
  "source_basis": ["chunk_id"],
  "review_status": "pending",
  "allowed_use": "lab|staging|prod_candidate"
}
```

## 5. Promotion rule

Synthetic samples may enter production training only if:

- they are explanatory, not source text;
- source basis is Z2;
- reviewer approved;
- copyright similarity check passed;
- NyayaBench sample validation passed.

## 6. Teacher-model-assisted data

The phrase `teacher-model-assisted draft data` is canonical. Do not call teacher-model output “truth”, “scripture”, or “authority”.

## 7. Synthetic eval traps

Synthetic adversarial cases are allowed and encouraged for:

- fake shloka detection;
- no-source refusals;
- citation mismatch;
- sectarian absolutism;
- unsafe ritual prompts.

## 8. Auditability

All synthetic generation runs must store:

```text
prompt version
generator model
temperature/settings
source pack
output hash
review status
```
