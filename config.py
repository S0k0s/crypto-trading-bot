from pydantic_settings import BaseSettings
from typing import List, Optional

class Settings(BaseSettings):
    # API Keys
    OPENAI_API_KEY: Optional[str] = None
    DUNE_API_KEY: Optional[str] = None
    COINGECKO_API_KEY: Optional[str] = None
    
    # Database
    DATABASE_URL: str = "sqlite:///./trading.db"
    
    # Risk Defaults
    DEFAULT_RISK_PER_TRADE_PCT: float = 1.0
    MAX_PORTFOLIO_HEAT_PCT: float = 6.0
    
    # Alert Thresholds
    EXCHANGE_INFLOW_THRESHOLD_MULTIPLIER: float = 3.0
    TVL_DROP_THRESHOLD_PCT: float = 20.0
    SMART_MONEY_FLOW_THRESHOLD: float = 100000  # USD
    
    # Polling Intervals (seconds)
    NEWS_POLL_INTERVAL: int = 300  # 5 minutes
    ONCHAIN_POLL_INTERVAL: int = 60  # 1 minute
    
    # Market Cycle Detection
    BTC_DOMINANCE_ACCUMULATION: float = 50.0
    BTC_DOMINANCE_MARKUP: float = 45.0
    BTC_DOMINANCE_DISTRIBUTION: float = 55.0
    
    class Config:
        env_file = ".env"

settings = Settings()
