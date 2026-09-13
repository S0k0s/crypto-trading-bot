from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List

import httpx

LLAMA_URL = "https://api.llama.fi"


class DefiLlamaClient:
    async def chains_tvl(self) -> List[Dict[str, Any]]:
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.get(f"{LLAMA_URL}/v2/chains")
            response.raise_for_status()
            rows = response.json()

        selected = {"Ethereum", "Solana", "Arbitrum", "Base", "Bitcoin"}

        return [
            {
                "name": row.get("name"),
                "tvl_usd": row.get("tvl"),
                "token_symbol": row.get("tokenSymbol"),
                "change_1d_pct": row.get("change_1d"),
                "change_7d_pct": row.get("change_7d"),
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }
            for row in rows
            if row.get("name") in selected
        ]
