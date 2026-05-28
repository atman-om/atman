#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Download/cache Qwen model files via huggingface_hub.")
    parser.add_argument("--model-id", default=os.getenv("ATMAN_QWEN_MODEL_ID", "Qwen/Qwen3-14B"))
    parser.add_argument("--cache-dir", default=os.getenv("ATMAN_QWEN_MODEL_CACHE_DIR", "./generated/models/qwen"))
    parser.add_argument("--allow-pattern", action="append", default=["*.json", "*.model", "*.safetensors", "tokenizer*"], help="Hugging Face allow-pattern; repeatable")
    args = parser.parse_args()
    try:
        from huggingface_hub import snapshot_download
    except ImportError:
        print("Install huggingface_hub first: pip install huggingface_hub")
        return 2
    cache_dir = Path(args.cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)
    path = snapshot_download(repo_id=args.model_id, cache_dir=str(cache_dir), allow_patterns=args.allow_pattern)
    print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
