# Atman Repo v1.0 — Production Release

Atman is a Hindi-first, source-governed Dharma AI platform. v1.0 consolidates the skipped v0.8 and v0.9 layers into one production release candidate:

- v0.8: web-to-corpus, crawler governance, OCR analysis, source-quality scoring, provenance ledger.
- v0.9: Qwen dataset builder, LoRA/QLoRA run planner, checkpoint registry, model release gate, serving profiles.
- v1.0: production readiness, ops runbook, backup simulation, incident ledger, Studio/public app, corpus review, content factory, NyayaBench, source explorer.

## Run

```bash
cp .env.example .env
docker compose up --build
```

## URLs

```text
API:        http://localhost:8000/docs
Studio:     http://localhost:3000
Public App: http://localhost:3001
Qdrant:     http://localhost:6333/dashboard
MinIO:      http://localhost:9001
```

## v1.0 endpoint groups

```text
/ocr/*
/web-to-corpus/*
/training/*
/ops/*
/eval/*
/public/*
/corpus/*
/content/*
/source-explorer/*
/runtime/*
```

## Boundary

This repo is runnable and production-structured, but it does not bundle Qwen model weights or a production-reviewed Dharma corpus. Real Qwen serving is configured via an OpenAI-compatible Qwen server.
