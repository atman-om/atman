from __future__ import annotations

import json
import sys
from urllib import request

API = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"


def post(path: str, payload: dict) -> dict:
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = request.Request(f"{API}{path}", data=data, headers={"Content-Type": "application/json"}, method="POST")
    with request.urlopen(req, timeout=30) as res:  # noqa: S310 - local smoke script
        return json.loads(res.read().decode("utf-8"))


def main() -> None:
    session = post("/chat/sessions", {"title": "Smoke Chat", "mode": "simple", "language": "hi", "citation_mode": "hidden"})
    turn = post(f"/chat/sessions/{session['id']}/messages", {"message": "कर्म योग क्या है?", "top_k": 3, "citation_mode": "hidden"})
    print(json.dumps({"session_id": session["id"], "assistant_preview": turn["assistant_message"]["content"][:300], "usage": turn["assistant_message"].get("usage")}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
