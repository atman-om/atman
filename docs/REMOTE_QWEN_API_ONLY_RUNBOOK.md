# Remote Qwen API Only Runbook

## Decision

The model is remote. Atman does not download, host, or fine-tune Qwen in the default v1.0.5 path.

## Required Environment

```env
ATMAN_QWEN_RUNTIME_MODE=openai_compatible
ATMAN_QWEN_MODEL_ID=qwen-plus
ATMAN_QWEN_BASE_URL=https://dashscope-intl.aliyuncs.com/compatible-mode/v1
ATMAN_QWEN_API_KEY=replace_with_remote_qwen_api_key
```

## Request Flow

```text
chat UI → Atman API → corpus/RAG → remote Qwen API → verifier/safety → response
```

## Cost Controls

Configure optional estimates:

```env
ATMAN_REMOTE_QWEN_COST_PER_1K_INPUT_TOKENS_USD=0.0
ATMAN_REMOTE_QWEN_COST_PER_1K_OUTPUT_TOKENS_USD=0.0
```

Then inspect:

```text
GET /models/remote/usage/summary
GET /analytics/overview
```

## Failure Behavior

If the remote endpoint fails, the existing Qwen runtime facade falls back to deterministic local output. This is acceptable for development, not for production launch.
