# Qwen Runtime Runbook

## Runtime modes

| Mode | Purpose | External dependency |
|---|---|---:|
| `deterministic` | local/offline smoke tests | none |
| `openai_compatible` | production-style Qwen server | vLLM/Ollama/LM Studio/TGI |
| `transformers` | direct Hugging Face local model | torch/transformers + GPU |

## Health check

```bash
curl http://localhost:8000/runtime/status
```

## Internal chat check

```bash
curl -X POST http://localhost:8000/runtime/qwen/chat \
  -H 'Content-Type: application/json' \
  -d '{"messages":[{"role":"user","content":"कर्मयोग क्या है?"}]}'
```

## Safety invariant

Qwen output is never directly released as final Dharma authority. The runtime response remains downstream of:

```text
retrieval → generation → safety check → citation display → user-visible answer
```

## Release rule

`Atman-Lab-Qwen-*` can be used in lab/runtime. `Atman-Prod` is blocked until NyayaBench and release gates pass.
