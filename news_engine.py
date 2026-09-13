from __future__ import annotations
from typing import Dict

KEYWORDS = {
    "supply": ["halving", "unlock", "burn", "issuance", "inflation", "buyback", "vesting"],
    "utility": ["mainnet", "adoption", "users", "fees", "revenue", "integration", "partnership"],
    "liquidity": ["listing", "etf", "inflow", "outflow", "market maker", "liquidation", "volume"],
    "trust": ["hack", "exploit", "rug", "fraud", "lawsuit", "insolvency", "ftx", "depeg"],
    "technology": ["upgrade", "outage", "fork", "security", "validator", "bug", "release"],
}

def classify_headline(headline: str) -> Dict[str, object]:
    text = headline.lower()
    matched = {category: [word for word in words if word in text] for category, words in KEYWORDS.items()}
    matched = {k: v for k, v in matched.items() if v}
    primary = max(matched, key=lambda key: len(matched[key])) if matched else "unclassified"
    direction = "negative" if "trust" in matched else ("positive" if matched else "unclear")
    return {"primary_class": primary, "matches": matched, "direction": direction}

def analyze_event(headline: str, pre_move_pct_1h: float, surprise_score: float, source_reliability: float, volume_multiple: float, account_equity: float, normal_risk_pct: float = 1.0, entry: float | None = None, stop: float | None = None, target: float | None = None) -> Dict[str, object]:
    classification = classify_headline(headline)
    catalyst = min(1.0, max(0.0, 0.35 * surprise_score + 0.35 * source_reliability + 0.30 * min(volume_multiple / 3, 1)))
    priced_in = abs(pre_move_pct_1h) >= (8 + catalyst * 10)
    size_factor = 0.5 if priced_in else (1.0 if catalyst >= 0.7 else 0.75)
    risk_amount = account_equity * normal_risk_pct / 100 * size_factor
    result = {**classification, "catalyst_score": round(catalyst, 2), "priced_in_risk": priced_in, "sizing_adjustment_pct": round(size_factor * 100, 0), "active_risk_amount": round(risk_amount, 2), "method": "Event → expectations → liquidity → leverage → price reaction"}
    if entry and stop and target and entry != stop:
        stop_distance = abs(entry - stop)
        units = risk_amount / stop_distance
        potential_profit = abs(target - entry) * units
        result["trade_scenario"] = {"position_units": round(units, 6), "notional": round(units * entry, 2), "loss_at_stop": round(risk_amount, 2), "profit_at_target": round(potential_profit, 2), "r_multiple": round(potential_profit / risk_amount, 2) if risk_amount else 0}
    return result
