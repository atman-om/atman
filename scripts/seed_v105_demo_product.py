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
    user = post("/accounts/users", {"email": "owner@atman.local", "display_name": "Atman Owner", "role": "owner", "preferences": {"language": "hi"}})
    channel = post("/publishing/channels", {"name": "Manual Website Export", "channel_type": "manual_export", "config": {"review_required": True}})
    pub = post("/publishing/items", {"title": "Daily Wisdom Seed", "body": "कर्म और साधना पर पहला demo publication draft.", "status": "DRAFT", "channel_id": channel["id"]})
    acq = post("/acquisition/jobs", {"source_uri": "https://example.org/bhagavad-gita", "mode": "wide_discovery", "discovered_title": "Bhagavad Gita discovery seed", "extracted_text": "Bhagavad Gita गीता वेद उपनिषद कर्म योग " * 100, "rights_signal": "PUBLIC_DOMAIN_VERIFIED"})
    print(json.dumps({"user": user["id"], "channel": channel["id"], "publication": pub["id"], "acquisition": acq["id"]}, indent=2))


if __name__ == "__main__":
    main()
