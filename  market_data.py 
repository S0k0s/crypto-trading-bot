from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any, Dict, List

import httpx

COINGECKO_URL = "https://api.coingecko.com/api/v3"
COIN_IDS = {"BTC": "bitcoin", "ETH": "ethereum", "SOL": "solana"}


class MarketDataClient:
    def __init__(self) -> None:
        self.api_key = os.getenv("COINGECKO_API_KEY")

    def _headers(self) -> Dict[str, str]:
        if self.api_key:
            return {"x-cg-demo-api-key": self.api_key}
        return {}

    async def live_market(self) -> List[Dict[str, Any]]:
        params = {
            "vs_currency": "usd",
            "ids": ",".join(COIN_IDS.values()),
            "order": "market_cap_desc",
            "per_page": 3,
            "page": 1,
            "sparkline": "false",
            "price_change_percentage": "7d,30d",
        }

        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.get(
                f"{COINGECKO_URL}/coins/markets",
                params=params,
                headers=self._headers(),
            )
            response.raise_for_status()
            rows = response.json()

        reverse = {coin_id: symbol for symbol, coin_id in COIN_IDS.items()}

        return [
            {
                "symbol": reverse.get(row["id"], row["symbol"].upper()),
                "coin_id": row["id"],
                "price_usd": row.get("current_price"),
                "market_cap_usd": row.get("market_cap"),
                "volume_24h_usd": row.get("total_volume"),
                "change_24h_pct": row.get("price_change_percentage_24h"),
                "change_7d_pct": row.get("price_change_percentage_7d_in_currency"),
                "change_30d_pct": row.get("price_change_percentage_30d_in_currency"),
                "ath_usd": row.get("ath"),
                "ath_change_pct": row.get("ath_change_percentage"),
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }
            for row in rows
        ]

    async def history(self, symbol: str, days: int = 30) -> Dict[str, Any]:
        coin_id = COIN_IDS.get(symbol.upper())
        if not coin_id:
            raise ValueError("Supported assets: BTC, ETH, SOL")

        params = {
            "vs_currency": "usd",
            "days": max(1, min(days, 365)),
            "interval": "daily",
        }

        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.get(
                f"{COINGECKO_URL}/coins/{coin_id}/market_chart",
                params=params,
                headers=self._headers(),
            )
            response.raise_for_status()
            data = response.json()

        prices = [
            {"timestamp": point[0], "price": point[1]}
            for point in data.get("prices", [])
        ]

        return {
            "symbol": symbol.upper(),
            "days": days,
            "prices": prices,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
        }
