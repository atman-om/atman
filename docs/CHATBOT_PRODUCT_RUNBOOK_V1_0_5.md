# Chatbot Product Runbook v1.0.5

## User Modes

- `simple`: Hindi-first general answer.
- `source`: shows compact source references.
- `scholar`: exposes internal evidence trail.
- `teacher`: optimized for educational explanation.
- `admin_debug`: exposes traces and model/cost metadata.

## Citation Modes

- `hidden`: no public citations, internal evidence retained.
- `source`: source title + locator visible.
- `scholar`: full evidence packet visible.

## Core Chat Tables

- `chat_sessions`
- `chat_messages`
- `chat_retrieval_traces`
- `chat_feedback`
- `model_usage_logs`

## Launch Checks

1. Remote Qwen endpoint configured.
2. Canonical corpus seeded.
3. `/analytics/readiness` has no blockers.
4. Chat feedback is enabled.
5. Cost logging is visible.
