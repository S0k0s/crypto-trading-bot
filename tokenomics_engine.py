from __future__ import annotations
from typing import Dict

TOKENOMICS = {
    "BTC": {"supply_model": "Hard cap / halving", "demand_link": "Settlement and monetary demand", "primary_watch": "New supply, liquidity, miner economics", "base_score": 76},
    "ETH": {"supply_model": "Validator issuance minus EIP-1559 burn", "demand_link": "Gas, settlement and blockspace", "primary_watch": "Burn versus issuance, fees, L2 value capture", "base_score": 70},
    "SOL": {"supply_model": "Disinflationary issuance minus fee burn", "demand_link": "Applications, throughput and fee activity", "primary_watch": "Inflation, fee offset, activity quality, reliability", "base_score": 62},
}

def net_supply_signal(issuance: float, burn: float) -> Dict[str, float | str]:
    net = issuance - burn
    label = "deflationary_pressure" if net < 0 else ("neutral" if net == 0 else "dilution_pressure")
    return {"net_supply_change": net, "signal": label}

def asset_tokenomics(symbol: str, usage_score: float = 3, liquidity_score: float = 3, risk_score: float = 3) -> Dict[str, object]:
    symbol = symbol.upper()
    profile = TOKENOMICS.get(symbol)
    if not profile:
        raise ValueError("Supported assets: BTC, ETH, SOL")
    score = max(0, min(100, profile["base_score"] + (usage_score - 3) * 6 + (liquidity_score - 3) * 5 - (risk_score - 3) * 7))
    scenario = "constructive" if score >= 75 else ("balanced" if score >= 55 else "fragile")
    return {**profile, "symbol": symbol, "score": round(score, 1), "scenario": scenario, "formula": "Price impact ≈ supply dynamics × demand × liquidity × expectations"}
