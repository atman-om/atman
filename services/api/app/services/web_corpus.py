from __future__ import annotations
from dataclasses import dataclass
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser
import hashlib

import httpx
from bs4 import BeautifulSoup
from sqlalchemy.ext.asyncio import AsyncSession

from services.api.app.core.config import Settings
from services.api.app.models import WebSource
from services.api.app.domain.enums import RightsStatus


@dataclass(frozen=True)
class RobotsResult:
    status: str
    robots_url: str | None
    reason: str | None = None


async def check_robots(url: str, *, user_agent: str = "AtmanBot/0.3") -> RobotsResult:
    parsed = urlparse(url)
    if not parsed.scheme or not parsed.netloc:
        return RobotsResult(status="INVALID_URL", robots_url=None, reason="URL missing scheme or host")
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    try:
        async with httpx.AsyncClient(timeout=8.0, follow_redirects=True) as client:
            response = await client.get(robots_url)
        if response.status_code >= 400:
            return RobotsResult(status="UNKNOWN", robots_url=robots_url, reason=f"robots status {response.status_code}")
        parser = RobotFileParser()
        parser.parse(response.text.splitlines())
        allowed = parser.can_fetch(user_agent, url)
        return RobotsResult(status="ALLOWED" if allowed else "DISALLOWED", robots_url=robots_url)
    except Exception as exc:
        return RobotsResult(status="UNKNOWN", robots_url=robots_url, reason=str(exc))


async def fetch_extract_text(url: str) -> tuple[str | None, str | None, str | None]:
    async with httpx.AsyncClient(timeout=20.0, follow_redirects=True) as client:
        response = await client.get(url, headers={"User-Agent": "AtmanBot/0.3"})
        response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    title = soup.title.string.strip() if soup.title and soup.title.string else None
    for tag in soup(["script", "style", "noscript", "nav", "footer", "header"]):
        tag.decompose()
    text = "\n".join(line.strip() for line in soup.get_text("\n").splitlines() if line.strip())
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest() if text else None
    return title, text, digest


async def register_web_source(
    session: AsyncSession,
    *,
    url: str,
    rights_status: RightsStatus,
    fetch_now: bool,
    settings: Settings,
) -> WebSource:
    robots = await check_robots(url)
    extracted_text = None
    title = None
    digest = None
    quality_score = 0.0
    if fetch_now:
        if not settings.enable_network_crawl:
            raise PermissionError("Network crawl is disabled. Set ATMAN_ENABLE_NETWORK_CRAWL=true after rights review.")
        if robots.status == "DISALLOWED":
            raise PermissionError("robots.txt disallows crawling this URL")
        title, extracted_text, digest = await fetch_extract_text(url)
        quality_score = min(1.0, len(extracted_text or "") / 8000.0)
    row = WebSource(
        url=url,
        title=title,
        robots_status=robots.status,
        tos_status="UNKNOWN",
        rights_status=rights_status.value,
        content_hash=digest,
        extracted_text=extracted_text,
        quality_score=quality_score,
        provenance={"robots_url": robots.robots_url, "robots_reason": robots.reason},
    )
    session.add(row)
    await session.commit()
    await session.refresh(row)
    return row
