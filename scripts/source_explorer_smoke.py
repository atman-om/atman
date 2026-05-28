from __future__ import annotations

import argparse
import httpx


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://localhost:8000")
    parser.add_argument("--query", default="कर्म")
    args = parser.parse_args()
    response = httpx.get(f"{args.base_url}/public/source-explorer/search", params={"q": args.query, "limit": 10}, timeout=20)
    response.raise_for_status()
    print(response.text)


if __name__ == "__main__":
    main()
