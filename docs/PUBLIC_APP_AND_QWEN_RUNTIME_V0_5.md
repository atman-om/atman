# Atman Repo v0.5 — Public App and Qwen Runtime

## Scope

v0.5 turns the v0.4 governed content factory into a user-facing platform scaffold.

Added:

- Public Next.js app at `apps/public`.
- Public API routes under `/public`.
- Qwen runtime facade under `/runtime`.
- Deterministic offline fallback for local development.
- OpenAI-compatible runtime integration for vLLM/Ollama/LM Studio/TGI deployments.
- Runtime status endpoint.
- Streaming public ask endpoint scaffold.

## Boundary

Qwen weights are **not bundled**. This repo is runtime-ready, not model-weight-distribution.

Default mode:

```bash
ATMAN_QWEN_RUNTIME_MODE=deterministic
```

Production-style mode:

```bash
ATMAN_QWEN_RUNTIME_MODE=openai_compatible
ATMAN_QWEN_MODEL_ID=Qwen/Qwen3-14B
ATMAN_QWEN_BASE_URL=http://qwen-runtime:8001
```

The Qwen server must expose `/v1/chat/completions`.
