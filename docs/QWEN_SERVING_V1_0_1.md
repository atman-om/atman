# Qwen Serving — Atman v1.0.1

## What changed

v1.0 had a Qwen runtime connector. v1.0.1 adds first-class serving profiles:

```text
Deterministic fallback  → no weights, app smoke tests only
vLLM Qwen server       → GPU OpenAI-compatible serving
Ollama Qwen server     → local OpenAI-compatible serving
LM Studio/TGI/custom   → supported through ATMAN_QWEN_BASE_URL
```

## Run deterministic mode

```bash
cp .env.example .env
docker compose up --build
```

## Run vLLM Qwen profile

```bash
export HF_TOKEN=...
export ATMAN_QWEN_MODEL_ID=Qwen/Qwen3-14B
docker compose -f docker-compose.yml -f docker-compose.qwen.yml --profile qwen-vllm up --build
```

Set API env:

```env
ATMAN_QWEN_RUNTIME_MODE=openai_compatible
ATMAN_QWEN_BASE_URL=http://qwen-vllm:8000/v1
```

## Run Ollama profile

```bash
./scripts/serve_qwen_ollama.sh
```

Set API env:

```env
ATMAN_QWEN_RUNTIME_MODE=openai_compatible
ATMAN_QWEN_BASE_URL=http://qwen-ollama:11434/v1
ATMAN_QWEN_MODEL_ID=qwen3:14b
```

## API checks

```text
GET  /qwen/serving/profiles
GET  /qwen/serving/status
POST /qwen/serving/smoke-test
```

## Boundary

The repo still does not bundle Qwen weights. It provides deployable server profiles and wiring.
