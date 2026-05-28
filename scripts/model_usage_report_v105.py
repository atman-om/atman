from __future__ import annotations

import json
import sys
from urllib import request

API = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"


def get(path: str) -> dict:
    with request.urlopen(f"{API}{path}", timeout=30) as res:  # noqa: S310 - local smoke script
        return json.loads(res.read().decode("utf-8"))


if __name__ == "__main__":
    print(json.dumps({"usage": get("/models/remote/usage/summary"), "overview": get("/analytics/overview")}, indent=2, ensure_ascii=False))
