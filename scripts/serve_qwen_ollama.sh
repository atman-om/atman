#!/usr/bin/env bash
set -euo pipefail
MODEL="${ATMAN_QWEN_OLLAMA_MODEL:-qwen3:14b}"
docker compose -f docker-compose.yml -f docker-compose.qwen.yml --profile qwen-ollama up -d qwen-ollama
sleep 3
docker exec -it "$(docker compose -f docker-compose.yml -f docker-compose.qwen.yml ps -q qwen-ollama)" ollama pull "${MODEL}"
