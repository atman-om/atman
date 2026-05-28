from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urlparse
import hashlib

import httpx
from bs4 import BeautifulSoup

from services.api.app.domain.enums import RightsStatus
from services.api.app.services.web_quality import score_web_source_text


@dataclass(frozen=True)
class CrawlExecution:
    status: str
    robots_status: str
    fetched_bytes: int
    extracted_text: str | None
    extracted_text_hash: str | None
    quality_score: float
    error: str | None
    result: dict[str, object]


def extract_article_text(html: str) -> tuple[str | None, str]:
    soup = BeautifulSoup(html, "html.parser")
    title = soup.title.string.strip() if soup.title and soup.title.string else None
    for tag in soup(["script", "style", "noscript", "nav", "footer", "header", "aside"]):
        tag.decompose()
    candidates = soup.find_all(["article", "main"])
    raw = "\n".join(c.get_text("\n") for c in candidates) if candidates else soup.get_text("\n")
    text = "\n".join(line.strip() for line in raw.splitlines() if line.strip())
    return title, text


async def execute_crawl(url: str, *, rights_status, settings, force: bool = False) -> CrawlExecution:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return CrawlExecution("INVALID_URL", "INVALID_URL", 0, None, None, 0.0, "URL must be http(s)", {})
    from services.api.app.services.web_corpus import check_robots

    robots = await check_robots(url, user_agent=settings.crawler_user_agent)
    if robots.status == "DISALLOWED" and not force:
        return CrawlExecution("BLOCKED_ROBOTS", robots.status, 0, None, None, 0.0, "robots.txt disallows crawl", {"robots_url": robots.robots_url})
    if settings.crawler_require_rights_for_fetch and rights_status == RightsStatus.UNKNOWN and not force:
        return CrawlExecution("BLOCKED_RIGHTS", robots.status, 0, None, None, 0.0, "rights review required before fetch", {"robots_url": robots.robots_url})
    if not settings.enable_network_crawl and not force:
        return CrawlExecution("BLOCKED_NETWORK_DISABLED", robots.status, 0, None, None, 0.0, "network crawl disabled", {"robots_url": robots.robots_url})
    try:
        async with httpx.AsyncClient(timeout=settings.crawler_timeout_seconds, follow_redirects=True) as client:
            response = await client.get(url, headers={"User-Agent": settings.crawler_user_agent})
            response.raise_for_status()
            html = response.text[: settings.crawler_max_bytes]
    except Exception as exc:  # pragma: no cover - network disabled in tests by design
        return CrawlExecution("FETCH_FAILED", robots.status, 0, None, None, 0.0, str(exc), {"robots_url": robots.robots_url})
    title, text = extract_article_text(html)
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest() if text else None
    assessment = score_web_source_text(text or "", url=url, rights_status=rights_status.value, robots_status=robots.status)
    return CrawlExecution(
        "EXTRACTED" if text else "EMPTY",
        robots.status,
        len(html.encode("utf-8")),
        text,
        digest,
        assessment.score,
        None,
        {"title": title, "robots_url": robots.robots_url, "quality": assessment.components, "allowed_usage": assessment.allowed_usage},
    )


async def create_crawl_job(
    session,
    *,
    url: str,
    rights_status,
    fetch_now: bool,
    force: bool,
    settings,
) -> CrawlJob:
    from services.api.app.models import CrawlJob, ProvenanceEvent

    execution = None
    if fetch_now:
        execution = await execute_crawl(url, rights_status=rights_status, settings=settings, force=force)
    row = CrawlJob(
        url=url,
        status=execution.status if execution else "REGISTERED",
        robots_status=execution.robots_status if execution else "UNKNOWN",
        rights_status=rights_status.value,
        fetch_requested=fetch_now,
        fetched_bytes=execution.fetched_bytes if execution else 0,
        extracted_text_hash=execution.extracted_text_hash if execution else None,
        quality_score=execution.quality_score if execution else 0.0,
        error=execution.error if execution else None,
        result=execution.result if execution else {"message": "registered for later fetch"},
    )
    session.add(row)
    await session.flush()
    session.add(ProvenanceEvent(object_type="crawl_job", object_id=row.id, event_type="CRAWL_REGISTERED", evidence={"url": url, "fetch_now": fetch_now, "force": force}))
    await session.commit()
    await session.refresh(row)
    return row
