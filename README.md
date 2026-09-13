# Crypto Research Dashboard

A mobile-friendly research dashboard for market context, position sizing, tokenomics scenarios, news-impact calculations and early-token due diligence.

## What it does

- **Market reader:** evaluates a manual market-regime input through price change, relative volume and sentiment.
- **Tokenomics engine:** BTC/ETH/SOL conditional scorecards using `Supply dynamics × demand × liquidity × expectations`.
- **News-to-profit calculator:** classifies supply, utility, liquidity, trust or technology events; checks price move already made; adjusts risk and calculates an entry/stop/target scenario.
- **Position sizing:** calculates planned loss, units, notional exposure and R multiple.
- **Early-token due diligence:** checks contract verification, liquidity, holder concentration, team transparency, audit status, unlock risk, utility and community quality.
- **Journal API:** stores manual trade records. Do not treat SQLite on a free web service as durable storage.

## Run locally

```bash
python -m pip install -r requirements.txt
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

## Render

Build command:

```bash
python -m pip install -r requirements.txt
```

Start command:

```bash
python -m uvicorn main:app --host 0.0.0.0 --port $PORT
```

## Security

Never add a seed phrase, private key, wallet password, exchange password or withdrawal-capable API key to this app, GitHub or Render. The application intentionally has no wallet connection and no trade-execution endpoint.

## Data status

Version 2 starts with manual inputs and deterministic calculations. Live market/news/on-chain feeds and background monitoring should be added only after persistent storage and source validation are configured.
