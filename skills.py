from typing import Dict, List, Optional
from pydantic import BaseModel
from datetime import datetime
import math

class PositionSizeInput(BaseModel):
    account_equity: float
    risk_per_trade_pct: float = 1.0
    entry_price: float
    stop_price: float
    direction: str = "long"

class PositionSizeResult(BaseModel):
    stop_distance_pct: float
    risk_amount: float
    position_size_units: float
    notional_exposure: float
    r_planned: Optional[float] = None
    pnl_if_target: Optional[float] = None

def calculate_position_size(input_data: PositionSizeInput, target_price: Optional[float] = None) -> PositionSizeResult:
    if input_data.direction == "long":
        stop_distance = input_data.entry_price - input_data.stop_price
    else:
        stop_distance = input_data.stop_price - input_data.entry_price
    
    stop_distance_pct = abs(stop_distance) / input_data.entry_price
    risk_amount = input_data.account_equity * (input_data.risk_per_trade_pct / 100)
    
    if stop_distance != 0:
        position_size_units = risk_amount / stop_distance
    else:
        position_size_units = 0
    
    notional_exposure = position_size_units * input_data.entry_price
    
    r_planned = None
    pnl_if_target = None
    if target_price:
        if input_data.direction == "long":
            potential_profit = target_price - input_data.entry_price
        else:
            potential_profit = input_data.entry_price - target_price
        
        if stop_distance != 0:
            r_planned = potential_profit / stop_distance
            pnl_if_target = potential_profit * position_size_units
    
    return PositionSizeResult(
        stop_distance_pct=stop_distance_pct,
        risk_amount=risk_amount,
        position_size_units=position_size_units,
        notional_exposure=notional_exposure,
        r_planned=r_planned,
        pnl_if_target=pnl_if_target
    )

class NewsImpactInput(BaseModel):
    headline: str
    coin: str
    market_cap_rank: int
    pre_move_pct_1h: float
    sentiment_score: float = 0.5
    surprise_score: float = 0.5
    scope: str = "single_token"
    historical_avg_move_pct: Optional[float] = None

class NewsImpactResult(BaseModel):
    attention_score: float
    news_pressure: float
    expected_move_1h_pct: float
    sizing_adjustment_pct: float
    recommendation: str

def estimate_news_impact(input_data: NewsImpactInput) -> NewsImpactResult:
    attention_score = min(1.0, (len(input_data.headline) / 100) * input_data.surprise_score)
    
    scope_multiplier = {
        "single_token": 1.0,
        "sector": 1.3,
        "BTC": 1.5,
        "broad_risk": 1.7
    }.get(input_data.scope, 1.0)
    
    news_pressure = min(1.0, attention_score * scope_multiplier * input_data.sentiment_score)
    
    if input_data.historical_avg_move_pct:
        base_expected = input_data.historical_avg_move_pct
    else:
        if input_data.market_cap_rank < 20:
            base_expected = 8.0
        elif input_data.market_cap_rank < 100:
            base_expected = 12.0
        else:
            base_expected = 18.0
    
    expected_move_1h_pct = base_expected * (0.5 + 0.5 * (input_data.sentiment_score + input_data.surprise_score) / 2)
    
    if news_pressure > 0.7 and input_data.pre_move_pct_1h < expected_move_1h_pct * 0.5:
        sizing_adjustment_pct = 100.0
        recommendation = "Full position size - high conviction setup"
    elif input_data.pre_move_pct_1h > expected_move_1h_pct * 0.7:
        sizing_adjustment_pct = 50.0
        recommendation = "Reduce size 50% - likely mean reversion"
    else:
        sizing_adjustment_pct = 75.0
        recommendation = "Standard size with caution"
    
    return NewsImpactResult(
        attention_score=attention_score,
        news_pressure=news_pressure,
        expected_move_1h_pct=expected_move_1h_pct,
        sizing_adjustment_pct=sizing_adjustment_pct,
        recommendation=recommendation
    )

class TradeInput(BaseModel):
    trade_id: str
    symbol: str
    direction: str
    setup_type: str
    entry_price: float
    stop_price: float
    target_price: float
    position_size_units: float
    account_equity: float
    risk_per_trade_pct: float
    catalysts: Optional[List[str]] = None
    news_pressure_score: Optional[float] = None
    on_chain_signal: Optional[str] = None
    notes: Optional[str] = None

def calculate_trade_metrics(input_data: TradeInput) -> Dict:
    if input_data.direction == "long":
        stop_distance = input_data.entry_price - input_data.stop_price
        potential_profit = input_data.target_price - input_data.entry_price
    else:
        stop_distance = input_data.stop_price - input_data.entry_price
        potential_profit = input_data.entry_price - input_data.target_price
    
    risk_amount = input_data.account_equity * (input_data.risk_per_trade_pct / 100)
    r_planned = potential_profit / stop_distance if stop_distance != 0 else 0
    notional = input_data.position_size_units * input_data.entry_price
    
    return {
        "stop_distance": stop_distance,
        "stop_distance_pct": abs(stop_distance) / input_data.entry_price * 100,
        "risk_amount": risk_amount,
        "potential_profit": potential_profit,
        "r_planned": r_planned,
        "notional_exposure": notional,
        "leverage_ratio": notional / input_data.account_equity if input_data.account_equity > 0 else 0
    }

def get_market_cycle_phase(btc_dominance: float, market_sentiment: str = "neutral") -> str:
    if btc_dominance < 45 or market_sentiment == "extreme_fear":
        return "accumulation"
    elif 45 <= btc_dominance < 50 or market_sentiment == "neutral":
        return "markup"
    elif 50 <= btc_dominance < 55 or market_sentiment == "greed":
        return "distribution"
    else:
        return "markdown"

def get_allocation_recommendations(phase: str) -> Dict:
    allocations = {
        "accumulation": {
            "allocation_per_position_pct": [10, 15],
            "num_positions": [3, 5],
            "cash_stable_pct": [40, 60],
            "leverage": "none or very low"
        },
        "markup": {
            "allocation_per_position_pct": [5, 10],
            "num_positions": [4, 7],
            "cash_stable_pct": [20, 40],
            "leverage": "only high conviction, small"
        },
        "distribution": {
            "allocation_per_position_pct": [2, 5],
            "num_positions": [2, 4],
            "cash_stable_pct": [50, 70],
            "leverage": "avoid"
        },
        "markdown": {
            "allocation_per_position_pct": [3, 5],
            "num_positions": [2, 3],
            "cash_stable_pct": [70, 90],
            "leverage": "none"
        }
    }
    return allocations.get(phase, allocations["markup"])
