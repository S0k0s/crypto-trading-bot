from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Any, Dict

from defi_data import DefiLlamaClient
from market_data import MarketDataClient
from news_feeds import fetch_rss_news

cache: Dict[str, Any] = {
    "market": [],
    "defi": [],
    "news": [],
    "updated": {},
}


async def refresh_market() -> Dict[str, Any]:
    cache["market"] = await MarketDataClient().live_market()
    cache["updated"]["market"] = datetime.now(timezone.utc).isoformat()

    return {
        "count": len(cache["market"]),
        "updated_at": cache["updated"]["market"],
    }


async def refresh_defi() -> Dict[str, Any]:
    cache["defi"] = await DefiLlamaClient().chains_tvl()
    cache["updated"]["defi"] = datetime.now(timezone.utc).isoformat()

    return {
        "count": len(cache["defi"]),
        "updated_at": cache["updated"]["defi"],
    }


async def refresh_news() -> Dict[str, Any]:
    cache["news"] = await fetch_rss_news()
    cache["updated"]["news"] = datetime.now(timezone.utc).isoformat()

    return {
        "count": len(cache["news"]),
        "updated_at": cache["updated"]["news"],
    }


async def refresh_all() -> Dict[str, Any]:
    results = await asyncio.gather(
        refresh_market(),
        refresh_defi(),
        refresh_news(),
        return_exceptions=True,
    )

    labels = ["market", "defi", "news"]

    return {
        label: str(result) if isinstance(result, Exception) else result
        for label, result in zip(labels, results)
    }


async def polling_loop() -> None:
    while True:
        await refresh_all()
        await asyncio.sleep(300)
