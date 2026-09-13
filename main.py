from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import uuid

from config import settings
from database import get_db, Trade, Alert
from skills import (
    calculate_position_size, PositionSizeInput,
    estimate_news_impact, NewsImpactInput,
    calculate_trade_metrics, TradeInput,
    get_market_cycle_phase, get_allocation_recommendations
)
from schemas import PositionSizeRequest, NewsImpactRequest, TradeRequest, AlertResponse

app = FastAPI(title="Crypto Trading Bot", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {
        "status": "running",
        "service": "Crypto Trading Bot",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/api/position-size")
def position_size(request: PositionSizeRequest):
    input_data = PositionSizeInput(
        account_equity=request.account_equity,
        risk_per_trade_pct=request.risk_per_trade_pct,
        entry_price=request.entry_price,
        stop_price=request.stop_price,
        direction=request.direction
    )
    
    result = calculate_position_size(input_data, request.target_price)
    
    return {
        "success": True,
        "data": result.model_dump(),
        "recommendation": f"Risk ${result.risk_amount:.2f} ({request.risk_per_trade_pct}% of account) on this trade"
    }

@app.post("/api/news-impact")
def news_impact(request: NewsImpactRequest):
    input_data = NewsImpactInput(
        headline=request.headline,
        coin=request.coin,
        market_cap_rank=request.market_cap_rank,
        pre_move_pct_1h=request.pre_move_pct_1h,
        sentiment_score=request.sentiment_score,
        surprise_score=request.surprise_score,
        scope=request.scope,
        historical_avg_move_pct=request.historical_avg_move_pct
    )
    
    result = estimate_news_impact(input_data)
    
    return {
        "success": True,
        "data": result.model_dump(),
        "sizing_recommendation": f"Use {result.sizing_adjustment_pct}% of normal position size"
    }

@app.post("/api/trade")
def log_trade(request: TradeRequest, db: Session = Depends(get_db)):
    trade_input = TradeInput(
        trade_id=request.trade_id,
        symbol=request.symbol,
        direction=request.direction,
        setup_type=request.setup_type,
        entry_price=request.entry_price,
        stop_price=request.stop_price,
        target_price=request.target_price,
        position_size_units=request.position_size_units,
        account_equity=request.account_equity,
        risk_per_trade_pct=request.risk_per_trade_pct,
        catalysts=[request.catalysts] if request.catalysts else None,
        news_pressure_score=request.news_pressure_score,
        on_chain_signal=request.on_chain_signal,
        notes=request.notes
    )
    
    metrics = calculate_trade_metrics(trade_input)
    
    trade = Trade(
        trade_id=request.trade_id,
        symbol=request.symbol,
        direction=request.direction,
        setup_type=request.setup_type,
        entry_price=request.entry_price,
        stop_price=request.stop_price,
        target_price=request.target_price,
        position_size_units=request.position_size_units,
        notional_exposure=metrics["notional_exposure"],
        risk_per_trade_pct=request.risk_per_trade_pct,
        account_equity_at_entry=request.account_equity,
        r_planned=metrics["r_planned"],
        catalysts_present=request.catalysts,
        news_pressure_score=request.news_pressure_score,
        on_chain_signal=request.on_chain_signal,
        discipline_flag=request.discipline_flag,
        notes=request.notes
    )
    
    db.add(trade)
    db.commit()
    db.refresh(trade)
    
    return {
        "success": True,
        "message": "Trade logged successfully",
        "trade_id": trade.trade_id,
        "metrics": metrics
    }

@app.get("/api/journal")
def get_journal(limit: int = 50, db: Session = Depends(get_db)):
    trades = db.query(Trade).order_by(Trade.date_open.desc()).limit(limit).all()
    return [
        {
            "trade_id": t.trade_id,
            "symbol": t.symbol,
            "direction": t.direction,
            "setup_type": t.setup_type,
            "entry_price": t.entry_price,
            "exit_price": t.exit_price,
            "pnl_usd": t.pnl_usd,
            "r_realized": t.r_realized,
            "discipline_flag": t.discipline_flag,
            "date_open": t.date_open.isoformat() if t.date_open else None
        }
        for t in trades
    ]

@app.get("/api/alerts")
def get_alerts(active_only: bool = True, db: Session = Depends(get_db)):
    query = db.query(Alert)
    if active_only:
        query = query.filter(Alert.acknowledged == False)
    alerts = query.order_by(Alert.created_at.desc()).limit(50).all()
    return [
        {
            "id": a.id,
            "alert_type": a.alert_type,
            "symbol": a.symbol,
            "message": a.message,
            "severity": a.severity,
            "created_at": a.created_at.isoformat() if a.created_at else None,
            "acknowledged": a.acknowledged
        }
        for a in alerts
    ]

@app.post("/api/alerts/create")
def create_alert(
    alert_type: str,
    symbol: str,
    message: str,
    severity: str = "medium",
    db: Session = Depends(get_db)
):
    alert = Alert(
        alert_type=alert_type,
        symbol=symbol,
        message=message,
        severity=severity
    )
    db.add(alert)
    db.commit()
    return {"success": True, "alert_id": alert.id}

@app.get("/api/market-cycle")
def market_cycle(btc_dominance: Optional[float] = None, sentiment: Optional[str] = None):
    if btc_dominance is None:
        btc_dominance = 50.0
    if sentiment is None:
        sentiment = "neutral"
    
    phase = get_market_cycle_phase(btc_dominance, sentiment)
    allocation = get_allocation_recommendations(phase)
    
    return {
        "success": True,
        "phase": phase,
        "btc_dominance": btc_dominance,
        "sentiment": sentiment,
        "allocation": allocation
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
