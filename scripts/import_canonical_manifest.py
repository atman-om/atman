#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

import httpx


def main() -> int:
    parser = argparse.ArgumentParser(description="Import a canonical corpus manifest through Atman API.")
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--api", default=os.getenv("ATMAN_API_BASE", "http://localhost:8000"))
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    with httpx.Client(timeout=60) as client:
        response = client.post(args.api.rstrip("/") + "/canonical/import/manifest", json=manifest)
        response.raise_for_status()
        print(json.dumps(response.json(), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
