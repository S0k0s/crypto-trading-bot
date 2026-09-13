from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class PositionSizeRequest(BaseModel):
    account_equity: float
    risk_per_trade_pct: float = 1.0
    entry_price: float
    stop_price: float
    target_price: Optional[float] = None
    direction: str = "long"

class NewsImpactRequest(BaseModel):
    headline: str
    coin: str
    market_cap_rank: int
    pre_move_pct_1h: float
    sentiment_score: float = 0.5
    surprise_score: float = 0.5
    scope: str = "single_token"
    historical_avg_move_pct: Optional[float] = None

class TradeRequest(BaseModel):
    trade_id: str
    symbol: str
    direction: str
    setup_type: str
    entry_price: float
    stop_price: float
    target_price: float
    exit_price: Optional[float] = None
    position_size_units: float
    account_equity: float
    risk_per_trade_pct: float
    catalysts: Optional[str] = None
    news_pressure_score: Optional[float] = None
    on_chain_signal: Optional[str] = None
    discipline_flag: bool = True
    notes: Optional[str] = None

class AlertResponse(BaseModel):
    id: int
    alert_type: str
    symbol: str
    message: str
    severity: str
    created_at: datetime
    acknowledged: bool
    
    class Config:
        from_attributes = True
