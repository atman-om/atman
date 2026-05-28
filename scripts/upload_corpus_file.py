from __future__ import annotations

import argparse
from pathlib import Path

import httpx


def main() -> None:
    parser = argparse.ArgumentParser(description="Upload a corpus file to Atman v0.6")
    parser.add_argument("path", type=Path)
    parser.add_argument("--api", default="http://localhost:8000")
    parser.add_argument("--title", default=None)
    parser.add_argument("--language", default="hi")
    parser.add_argument("--rights-status", default="UNKNOWN")
    parser.add_argument("--locator", default=None)
    args = parser.parse_args()
    with args.path.open("rb") as handle:
        files = {"file": (args.path.name, handle, "application/octet-stream")}
        data = {
            "title": args.title or args.path.stem,
            "language": args.language,
            "rights_status": args.rights_status,
        }
        if args.locator:
            data["locator"] = args.locator
        response = httpx.post(f"{args.api}/corpus/upload", data=data, files=files, timeout=120)
    response.raise_for_status()
    print(response.text)


if __name__ == "__main__":
    main()
