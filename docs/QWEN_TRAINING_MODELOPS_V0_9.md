# v0.9 — Qwen Training and ModelOps

## Objective

Build Atman-Qwen adapters only from approved, provenance-tracked samples.

## Flow

```text
approved samples → dataset manifest → LoRA/QLoRA config → training run → checkpoint → NyayaBench → release gate → serving profile
```

## Default posture

Real GPU jobs are disabled by default. v1.0 includes a simulation-safe run path plus the registry and release-gate mechanics.

## Release rule

A checkpoint cannot become `Atman-Prod` unless eval score ≥ configured threshold and hard failures = 0.
