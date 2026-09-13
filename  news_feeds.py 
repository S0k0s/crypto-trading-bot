from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List
from xml.etree import ElementTree as ET

import httpx

RSS_FEEDS = [
    {
        "name": "CoinDesk",
        "url": "https://www.coindesk.com/arc/outboundfeeds/rss/",
    },
    {
        "name": "The Block",
        "url": "https://www.theblock.co/rss.xml",
    },
]


def get_text(node: Any, tag: str) -> str:
    element = node.find(tag)
    if element is not None and element.text:
        return element.text.strip()
    return ""


async def fetch_rss_news(limit: int = 30) -> List[Dict[str, str]]:
    articles: List[Dict[str, str]] = []

    async with httpx.AsyncClient(
        timeout=20,
        follow_redirects=True,
        headers={"User-Agent": "CryptoResearchDashboard/3.0"},
    ) as client:
        for feed in RSS_FEEDS:
            try:
                response = await client.get(feed["url"])
                response.raise_for_status()

                root = ET.fromstring(response.content)

                for item in root.findall(".//item"):
                    title = get_text(item, "title")
                    link = get_text(item, "link")
                    published = get_text(item, "pubDate")

                    if title and link:
                        articles.append(
                            {
                                "title": title,
                                "url": link,
                                "published": published,
                                "source": feed["name"],
                                "fetched_at": datetime.now(timezone.utc).isoformat(),
                            }
                        )
            except Exception:
                continue

    seen = set()
    unique = []

    for article in articles:
        if article["url"] not in seen:
            seen.add(article["url"])
            unique.append(article)

    return unique[:limit]
