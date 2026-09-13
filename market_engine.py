from __future__ import annotations

from typing import Dict, List

ASSET_PROFILE = {
    "BTC": {"supply_predictability": 5, "resilience": 5, "utility_growth": 3, "activity_dependence": 2, "liquidity": 5, "protocol_risk": 2},
    "ETH": {"supply_predictability": 3, "resilience": 3, "utility_growth": 5, "activity_dependence": 4, "liquidity": 4, "protocol_risk": 4},
    "SOL": {"supply_predictability": 2, "resilience": 2, "utility_growth": 5, "activity_dependence": 5, "liquidity": 3, "protocol_risk": 4},
}

def annualized_volatility(daily_returns: List[float]) -> float:
    if len(daily_returns) < 2:
        return 0.0
    mean = sum(daily_returns) / len(daily_returns)
    variance = sum((r - mean) ** 2 for r in daily_returns) / (len(daily_returns) - 1)
    return (variance ** 0.5) * (365 ** 0.5) * 100

def drawdown_from_peak(current_price: float, peak_price: float) -> float:
    if peak_price <= 0:
        return 0.0
    return ((current_price / peak_price) - 1) * 100

def market_regime(btc_change_24h: float, btc_volume_ratio: float, sentiment: str = "neutral") -> Dict[str, str]:
    score = 0
    score += 1 if btc_change_24h > 1 else (-1 if btc_change_24h < -1 else 0)
    score += 1 if btc_volume_ratio >= 1 else 0
    score += {"fear": -1, "extreme_fear": -2, "neutral": 0, "greed": 1, "extreme_greed": 1}.get(sentiment, 0)
    if score >= 2:
        return {"regime": "risk_on", "label": "Risk-on", "guidance": "Μην αυξάνεις θέση χωρίς stop, ακόμα και σε ισχυρό momentum."}
    if score <= -2:
        return {"regime": "risk_off", "label": "Risk-off", "guidance": "Μείωσε exposure και προτίμησε υψηλή ρευστότητα / μικρότερο sizing."}
    return {"regime": "neutral", "label": "Neutral", "guidance": "Επίλεξε μόνο setups με σαφή invalidation και επαρκές R/R."}

def asset_scorecard(symbol: str) -> Dict[str, int]:
    return ASSET_PROFILE.get(symbol.upper(), {})
