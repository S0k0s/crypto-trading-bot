from __future__ import annotations
from typing import Dict

def early_token_assessment(market_cap: float, liquidity: float, top_holder_pct: float, team_transparency: int, product_utility: int, audit_status: str, contract_verified: bool, unlock_risk: int, community_quality: int) -> Dict[str, object]:
    flags = []
    risk = 0
    if not contract_verified:
        risk += 30; flags.append("Contract not verified from an official source")
    if liquidity < 50000:
        risk += 20; flags.append("Low liquidity increases exit and slippage risk")
    if top_holder_pct > 25:
        risk += 15; flags.append("High holder concentration")
    if team_transparency <= 1:
        risk += 12; flags.append("Low team transparency / identity risk")
    if audit_status.lower() in {"none", "unknown"}:
        risk += 10; flags.append("No verified audit information")
    risk += max(0, unlock_risk - 3) * 3
    risk -= max(0, product_utility - 3) * 2
    risk -= max(0, community_quality - 3)
    risk = max(0, min(100, risk))
    label = "extreme" if risk >= 60 else ("high" if risk >= 35 else "moderate")
    multiples = None
    if market_cap > 0:
        multiples = {"to_1m": round(1000000 / market_cap, 2), "to_10m": round(10000000 / market_cap, 2), "to_100m": round(100000000 / market_cap, 2)}
    return {"risk_score": risk, "risk_label": label, "flags": flags, "market_cap_multiple_scenarios": multiples, "note": "Market-cap scenarios are arithmetic only; they are not probability estimates or price targets."}
