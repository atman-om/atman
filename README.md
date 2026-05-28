# Atman Platform v2.0 — Dharma Knowledge OS with Model Lab

Atman v2.0 is an app-first Dharma AI platform: remote-Qwen chatbot, canonical Dharma corpus, source-correctness engine, content studio, learning paths, analytics, and a parallel Model Lab for Qwen fine-tuning experiments.

## Fast Start

```bash
cp .env.example .env
# set ATMAN_QWEN_BASE_URL and ATMAN_QWEN_API_KEY for real remote Qwen
# fallback/scaffold routes still run without a real model endpoint
docker compose up --build
```

Open:

```text
Atman App:  http://localhost:3002
Studio:     http://localhost:3000
Public App: http://localhost:3001
API Docs:   http://localhost:8000/docs
```

## v2.0 adds

- Unified Dharma Knowledge OS status API: `/os/status`
- Learning paths and saved answers: `/learning/*`
- Claim evidence correctness engine: `/correctness/claims/check`
- Parallel Model Lab: `/model-lab/*`
- Model Lab dataset planning, experiment registry, readiness, comparison gates
- Source rule: scrape broadly, quarantine first, canonicalize narrowly, train only from approved data

## Core launch rule

```text
Remote Qwen powers the live product.
Atman-Qwen fine-tuning runs in parallel.
A fine-tuned adapter cannot replace production until eval gates pass.
```

## Important external dependencies

Still external/not bundled:

- Qwen model/API key
- production-reviewed Dharma corpus
- real production auth/payment provider
- hosted deployment infrastructure

## Useful APIs

```text
GET  /os/status
GET  /learning/paths
POST /correctness/claims/check
GET  /model-lab/readiness
POST /model-lab/dataset-plan
POST /model-lab/experiments
GET  /model-lab/comparison
```
