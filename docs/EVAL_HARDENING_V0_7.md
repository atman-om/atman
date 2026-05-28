# Atman v0.7 — Eval Hardening

## Decision

v0.7 upgrades NyayaBench from seed dataset integrity checks into a deterministic release-gate surface.

## New API surface

```text
POST /eval/run/hardened
GET  /eval/runs/{run_id}/results
POST /eval/citation/check
POST /eval/fake-shloka/check
```

## Hardened benchmark families

```text
citation_alignment
fake_shloka
ritual_safety
sampradaya_neutrality
runtime_policy
source_grounded_qa
```

## Release gate

An artifact is blocked when:

```text
hard failure count > 0
citation alignment pass-rate < 0.95
fake-shloka hard failures > 0
overall pass-rate < 0.92
```

## Boundary

The v0.7 grader is deterministic and conservative. It does not claim theological correctness. It detects release-blocking structural failures before LLM-judge or human-review layers are added.
