# Atman v2.0 — Dharma Knowledge OS with Model Lab

## Decision

Atman v2.0 is the first product-grade architecture where the live app and the fine-tuning lane run in parallel.

```text
Live product: remote Qwen API + RAG + chatbot + canonical corpus
Parallel R&D: Model Lab + dataset builder + LoRA/QLoRA plans + NyayaBench gates
```

## Non-negotiable invariant

Fine-tuning may run in parallel, but a fine-tuned Atman-Qwen adapter cannot replace remote Qwen in production until it passes:

- NyayaBench hardened evals
- citation alignment
- fake-shloka traps
- source-correctness gates
- human release approval

## v2.0 Product Surfaces

- Atman Chat
- ShrutiKosh Library
- Learn paths
- Content Studio
- Correctness Engine
- Model Lab
- Analytics
- Operations

## Corpus rule

Scrape widely, quarantine first, verify before canonical use, and train only from approved datasets.
