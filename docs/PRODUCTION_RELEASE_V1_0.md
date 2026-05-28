# v1.0 — Production Release Candidate

v1.0 consolidates all layers from v0.3 through v0.9.

## Required production switches

```text
ATMAN_PRODUCTION_MODE=true
ATMAN_PRODUCTION_REQUIRE_AUTH=true
ATMAN_JWT_SECRET=<rotated secret>
ATMAN_QWEN_RUNTIME_MODE=openai_compatible
ATMAN_QWEN_BASE_URL=<Qwen server>
```

## Production acceptance

- Public app runs.
- Studio runs.
- Corpus ingestion and review work.
- Web/OCR acquisition is gated.
- Qwen runtime is configured.
- NyayaBench blocks failed releases.
- Training data is provenance-bound.
- Ops readiness has no hard failures.
