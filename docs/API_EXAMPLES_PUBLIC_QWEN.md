# API Examples — v0.5 Public + Qwen

## Public ask

```bash
curl -X POST http://localhost:8000/public/ask \
  -H 'Content-Type: application/json' \
  -d '{"question":"गीता में कर्मयोग क्या है?","language":"hi","top_k":5,"mode":"simple"}'
```

## Runtime status

```bash
curl http://localhost:8000/runtime/status
```

## Streaming ask

```bash
curl -N -X POST http://localhost:8000/public/ask/stream \
  -H 'Content-Type: application/json' \
  -d '{"question":"कर्मयोग का सार बताइए","language":"hi","top_k":5}'
```
