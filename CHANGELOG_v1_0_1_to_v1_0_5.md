# Changelog — v1.0.1 → v1.0.5

## Added

- Remote-Qwen-first default runtime mode.
- Chatbot sessions, messages, feedback, retrieval traces, and admin debug API.
- Remote model gateway provider status, route selection, usage logs, and cost summaries.
- Account/role scaffold for Owner/Admin/Reviewer/Editor/Viewer workflows.
- Wide acquisition jobs for broad discovery → quarantine → candidate canonical flow.
- Publishing channels and publication queue.
- Analytics overview and product readiness endpoints.
- Unified Atman App pages for Chatbot, Analytics, Publishing, Acquisition, and Accounts.
- New docs/runbooks for remote-Qwen-only launch, chatbot product ops, acquisition, analytics/billing, and deployment.
- v1.0.5 migration `0009_v105_chatbot_accounts_publishing_analytics.py`.

## Changed

- Qwen runtime default changed from deterministic fallback to `openai_compatible` remote API mode.
- Atman App homepage is now product/readiness focused.
- README updated to v1.0.5 quick-start flow.

## Still External

- Qwen model weights.
- Production Qwen API credentials.
- Full production auth provider.
- Full verified Dharma corpus.
- Payment gateway integration.
