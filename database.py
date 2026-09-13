from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from config import settings

engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Trade(Base):
    __tablename__ = "trades"
    
    id = Column(Integer, primary_key=True, index=True)
    trade_id = Column(String, unique=True, index=True)
    date_open = Column(DateTime, default=datetime.utcnow)
    date_close = Column(DateTime, nullable=True)
    symbol = Column(String, index=True)
    direction = Column(String)  # long/short
    setup_type = Column(String)
    entry_price = Column(Float)
    stop_price = Column(Float)
    target_price = Column(Float)
    exit_price = Column(Float, nullable=True)
    position_size_units = Column(Float)
    notional_exposure = Column(Float)
    risk_per_trade_pct = Column(Float)
    account_equity_at_entry = Column(Float)
    pnl_usd = Column(Float, nullable=True)
    pnl_pct = Column(Float, nullable=True)
    r_planned = Column(Float)
    r_realized = Column(Float, nullable=True)
    fees_usd = Column(Float, default=0.0)
    funding_usd = Column(Float, default=0.0)
    slippage_estimate_pct = Column(Float, default=0.0)
    catalysts_present = Column(Text, nullable=True)
    news_pressure_score = Column(Float, nullable=True)
    on_chain_signal = Column(String, nullable=True)
    discipline_flag = Column(Boolean, default=True)
    notes = Column(Text, nullable=True)

class Alert(Base):
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    alert_type = Column(String, index=True)  # on_chain, news, price
    symbol = Column(String, index=True)
    message = Column(Text)
    severity = Column(String)  # low, medium, high
    created_at = Column(DateTime, default=datetime.utcnow)
    acknowledged = Column(Boolean, default=False)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
