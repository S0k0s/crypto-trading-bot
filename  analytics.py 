from __future__ import annotations

from math import log, sqrt
from typing import Dict, List


def history_metrics(prices: List[float]) -> Dict[str, float]:
    if len(prices) < 2:
        return {
            "return_pct": 0.0,
            "annualized_volatility_pct": 0.0,
            "max_drawdown_pct": 0.0,
        }

    returns = [
        log(prices[i] / prices[i - 1])
        for i in range(1, len(prices))
        if prices[i - 1] > 0 and prices[i] > 0
    ]

    mean = sum(returns) / len(returns) if returns else 0
    variance = (
        sum((value - mean) ** 2 for value in returns) / (len(returns) - 1)
        if len(returns) > 1
        else 0
    )

    peak = prices[0]
    max_drawdown = 0.0

    for price in prices:
        peak = max(peak, price)
        max_drawdown = min(max_drawdown, (price / peak - 1) * 100)

    return {
        "return_pct": round((prices[-1] / prices[0] - 1) * 100, 2),
        "annualized_volatility_pct": round(sqrt(variance) * sqrt(365) * 100, 2),
        "max_drawdown_pct": round(max_drawdown, 2),
    }
