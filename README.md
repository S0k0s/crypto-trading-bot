# Crypto Trading Bot

Crypto trading skills engine: position sizing, news impact estimator, on-chain alerts, trade journal.

## Features

- **Position Size Calculator**: Calculate optimal position size based on risk % and stop loss
- **News Impact Estimator**: Analyze news headlines and estimate price impact
- **On-Chain Alerts**: Monitor wallet flows, DEX volume, TVL changes
- **Trade Journal**: Log trades with R-multiples, PnL, discipline tracking
- **Portfolio Allocation**: Adjust allocation based on market cycle phase

## Quick Start

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export OPENAI_API_KEY="your-key-here"
export DUNE_API_KEY="your-key-here"
export DATABASE_URL="sqlite:///./trading.db"

# Run the server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Deploy to Cloud

1. **Render**: Connect this repo, set build command `pip install -r requirements.txt`, start command `uvicorn main:app --host 0.0.0.0 --port $PORT`
2. **Railway**: Connect repo, add environment variables, auto-deploy

## API Endpoints

- `GET /` - Health check
- `POST /api/position-size` - Calculate position size
- `POST /api/news-impact` - Estimate news impact
- `POST /api/trade` - Log a trade
- `GET /api/journal` - Get trade journal
- `GET /api/alerts` - Get active alerts
- `POST /api/alerts/configure` - Configure alert thresholds

## Environment Variables

- `OPENAI_API_KEY` - For LLM-based news analysis
- `DUNE_API_KEY` - For on-chain data
- `COINGECKO_API_KEY` - For news/market data (optional)
- `DATABASE_URL` - Database connection string

## Skills Template

See `skills_template.json` for the complete skills specification.
