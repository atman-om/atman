#!/usr/bin/env bash
set -euo pipefail
MODEL_ID="${ATMAN_QWEN_MODEL_ID:-Qwen/Qwen3-14B}"
PORT="${ATMAN_QWEN_PORT:-8001}"
docker run --rm --gpus all \
  -p "${PORT}:8000" \
  -e HUGGING_FACE_HUB_TOKEN="${HF_TOKEN:-}" \
  -v "${PWD}/generated/models/qwen:/root/.cache/huggingface" \
  "${ATMAN_QWEN_VLLM_IMAGE:-vllm/vllm-openai:latest}" \
  --model "${MODEL_ID}" \
  --served-model-name "${MODEL_ID}" \
  --host 0.0.0.0 \
  --port 8000
