# Atman v1.0.5 — Product App Release

## Purpose

v1.0.5 consolidates the previous staged roadmap into a single product-oriented release:

- v1.0.2 Remote Qwen chatbot product app
- v1.0.3 Wide corpus acquisition and source correctness lane
- v1.0.4 Content publishing and account scaffolding
- v1.0.5 Analytics, cost control, and production deployment readiness

## Product Principle

Atman is remote-Qwen-first. The platform owns corpus, prompts, RAG, source correctness, content review, analytics, and UI. Qwen is called through a remote OpenAI-compatible API.

## Primary Interface

- `apps/atman` is the unified product shell.
- `/chat` is the primary end-user interaction surface.
- `/canonical` is the ShrutiKosh canonical library.
- `/acquisition` is wide discovery / quarantine intake.
- `/publishing` is the reviewed-content publication queue.
- `/analytics` is product, model usage, corpus, publishing, and billing telemetry.

## Key Backend APIs

```text
POST /chat/sessions
POST /chat/sessions/{session_id}/messages
POST /chat/messages/{message_id}/feedback
GET  /chat/debug/{message_id}

GET  /models/remote/status
GET  /models/remote/usage
GET  /models/remote/usage/summary

POST /acquisition/jobs
GET  /acquisition/jobs

POST /publishing/channels
POST /publishing/items
POST /publishing/items/{publication_id}/publish

GET  /analytics/overview
GET  /analytics/readiness
```

## Boundary

This release still does not bundle Qwen weights. It is an app + gateway + corpus/review/analytics platform that expects a remote Qwen-compatible API endpoint.
