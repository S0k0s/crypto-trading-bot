from pathlib import Path
from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from database import get_db, Trade
from skills import calculate_position_size, PositionSizeInput, estimate_news_impact, NewsImpactInput, calculate_trade_metrics, TradeInput, get_market_cycle_phase, get_allocation_recommendations
from schemas import PositionSizeRequest, NewsImpactRequest, TradeRequest
from market_engine import market_regime, asset_scorecard
from tokenomics_engine import asset_tokenomics, net_supply_signal
from news_engine import analyze_event
from due_diligence import early_token_assessment

app = FastAPI(title="Crypto Research Dashboard", version="2.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
BASE_DIR = Path(__file__).resolve().parent
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

@app.get("/")
def dashboard(): return FileResponse(BASE_DIR / "static" / "index.html")
@app.get("/health")
def health(): return {"status":"running","service":"Crypto Research Dashboard","version":"2.0.0","timestamp":datetime.utcnow().isoformat()}
@app.post("/api/position-size")
def position_size(request: PositionSizeRequest):
    result = calculate_position_size(PositionSizeInput(account_equity=request.account_equity, risk_per_trade_pct=request.risk_per_trade_pct, entry_price=request.entry_price, stop_price=request.stop_price, direction=request.direction), request.target_price)
    return {"success":True,"data":result.model_dump(),"recommendation":f"Maximum planned loss: ${result.risk_amount:.2f}"}
@app.post("/api/news-impact")
def news_impact(request: NewsImpactRequest):
    result = estimate_news_impact(NewsImpactInput(**request.model_dump()))
    return {"success":True,"data":result.model_dump()}
@app.post("/api/market-regime")
def analyze_market_regime(payload: dict): return market_regime(float(payload.get("btc_change_24h",0)), float(payload.get("btc_volume_ratio",1)), str(payload.get("sentiment","neutral")))
@app.get("/api/scorecard/{symbol}")
def scorecard(symbol: str): return {"symbol":symbol.upper(),"scores":asset_scorecard(symbol)}
@app.post("/api/tokenomics")
def tokenomics(payload: dict):
    try: return asset_tokenomics(str(payload.get("symbol","BTC")), float(payload.get("usage_score",3)), float(payload.get("liquidity_score",3)), float(payload.get("risk_score",3)))
    except ValueError as e: raise HTTPException(status_code=400, detail=str(e))
@app.post("/api/net-supply")
def net_supply(payload: dict): return net_supply_signal(float(payload.get("issuance",0)), float(payload.get("burn",0)))
@app.post("/api/news-analyze")
def news_analyze(payload: dict): return analyze_event(**payload)
@app.post("/api/due-diligence")
def due_diligence(payload: dict): return early_token_assessment(**payload)
@app.post("/api/trade")
def log_trade(request: TradeRequest, db: Session = Depends(get_db)):
    trade_input = TradeInput(trade_id=request.trade_id, symbol=request.symbol, direction=request.direction, setup_type=request.setup_type, entry_price=request.entry_price, stop_price=request.stop_price, target_price=request.target_price, position_size_units=request.position_size_units, account_equity=request.account_equity, risk_per_trade_pct=request.risk_per_trade_pct, catalysts=[request.catalysts] if request.catalysts else None, news_pressure_score=request.news_pressure_score, on_chain_signal=request.on_chain_signal, notes=request.notes)
    metrics = calculate_trade_metrics(trade_input)
    trade = Trade(trade_id=request.trade_id,symbol=request.symbol,direction=request.direction,setup_type=request.setup_type,entry_price=request.entry_price,stop_price=request.stop_price,target_price=request.target_price,position_size_units=request.position_size_units,notional_exposure=metrics["notional_exposure"],risk_per_trade_pct=request.risk_per_trade_pct,account_equity_at_entry=request.account_equity,r_planned=metrics["r_planned"],catalysts_present=request.catalysts,news_pressure_score=request.news_pressure_score,on_chain_signal=request.on_chain_signal,discipline_flag=request.discipline_flag,notes=request.notes)
    db.add(trade); db.commit(); db.refresh(trade)
    return {"success":True,"trade_id":trade.trade_id,"metrics":metrics}
@app.get("/api/journal")
def get_journal(limit: int = 50, db: Session = Depends(get_db)):
    rows = db.query(Trade).order_by(Trade.date_open.desc()).limit(limit).all()
    return [{"trade_id":x.trade_id,"symbol":x.symbol,"direction":x.direction,"entry_price":x.entry_price,"r_planned":x.r_planned,"date_open":x.date_open.isoformat() if x.date_open else None} for x in rows]
@app.get("/api/market-cycle")
def market_cycle(btc_dominance: float = 50, sentiment: str = "neutral"):
    phase = get_market_cycle_phase(btc_dominance, sentiment)
    return {"phase":phase,"allocation":get_allocation_recommendations(phase)}
