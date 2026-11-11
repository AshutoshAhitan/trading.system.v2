# Trading System v2

A two-part Python pipeline for Indian markets (NSE/BSE): **fetch** market data into a database, then **analyse** it.

| Module | Purpose |
|---|---|
| [`instrumentDataFetching/`](instrumentDataFetching) | Pulls instruments, OHLCV, delivery data, fundamentals, sectors, trading activity, index data and F&O data from Zerodha (Kite), Yahoo Finance, NSE, Screener, etc., and stores it in PostgreSQL (SQLite also supported). |
| [`instrumentAnalysis/`](instrumentAnalysis) | Reads that data and computes technical indicators, fundamental metrics and market breadth. |

```
trading.system.v2/
├── instrumentDataFetching/
│   ├── main.py              # CLI entry point
│   ├── run.sh               # equities OHLCV fetch
│   ├── run.indices.sh       # indices / F&O / streaming
│   ├── ecosystem.config.js  # PM2 config for the tick stream
│   ├── config/              # per-dataset JSON config + database.json
│   ├── sql-scripts/         # table DDL and stored procedures
│   ├── scripts/             # one-off helper scripts
│   └── src/                 # Ohlcv, Delivery, Fundamentals, Indices, Sectors, ...
└── instrumentAnalysis/
    ├── main.py              # CLI entry point
    ├── run.sh               # daily equity analysis
    ├── run.indices.sh       # intraday index analysis
    ├── config/              # per-analysis JSON config + database.json
    └── src/                 # technical, fundamental, marketBreadth, Database
```

## Requirements

- Python 3.10+
- PostgreSQL (default) — or SQLite
- [TA-Lib](https://ta-lib.org/) C library (needed by `instrumentAnalysis`)
- Chrome/Chromedriver for Selenium-based scrapers
- A Zerodha Kite Connect account for instrument/OHLCV/stream data

## Setup

Each module has its own `requirements.txt`; use a virtualenv per module.

```bash
cd instrumentDataFetching   # or instrumentAnalysis
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

Create the database tables using the scripts in `instrumentDataFetching/sql-scripts/table` and the stored procedures in `sql-scripts/stored-procedure`.

Edit `config/database.json` in **both** modules:

```json
{
  "dbType": "postgres",
  "postgres": { "database": "equities", "host": "localhost", "port": 5432, "user": "...", "password": "..." },
  "sqlite":   { "database": "../db/equities.sqlite.db" }
}
```

> `config/database.json` holds credentials. Keep it out of version control (add it to `.gitignore`) and rotate the password if it has ever been committed or shared.

## Data fetching

```bash
cd instrumentDataFetching
python main.py -dataTobeFetched=<type> [-symbolList=A,B] [-debug-level=INFO]
```

`-dataTobeFetched` choices: `ohlcv`, `ohlcv.stream`, `instruments`, `instruments.liquidity`, `delivery`, `tradingActivity`, `sectors`, `fundamentals`, `indices`, `indices.constituent`, `indices.fno.ohlcv`.

Shortcuts:

```bash
./run.sh                          # equities OHLCV
./run.indices.sh [DEBUG_LEVEL]    # indices
./run.indices.sh fno INFO         # index F&O OHLCV
./run.indices.sh ohlcv.stream INFO
pm2 start ecosystem.config.js     # run the tick stream under PM2
```

## Analysis

```bash
cd instrumentAnalysis
python main.py -a=<analysis>[,<analysis>...] -t=<timeframe> [-symbolList='NIFTY 50'] [-l=true]
```

- `-a` choices:
  - Equities: `ta.equities.{volume,ma,volatility,zones,candlestick,pricerange,slope}`
  - Indices: `ta.indices.{ma,candlestick,heikinAshiCandlestick,heikinAshiMA,adx,oi}`
  - Fundamental: `fa.quarterly`, `fa.annualy`
  - Market breadth: `breadth.market`
- `-t` timeframe: `1wk`, `1d`, `60m`, `1m` (default `1d`)
- `-l=true` runs in a loop for live/intraday updates

Shortcuts:

```bash
./run.sh                 # daily equity MA + candlestick patterns
./run.indices.sh         # one-shot 1m index analysis
./run.indices.sh loop    # continuous analysis for NIFTY 50
```

Each analysis is driven by a JSON file under `config/` (e.g. `config/technical/equities/ma.json`).

## Typical workflow

1. Fetch instruments and OHLCV (`instrumentDataFetching`).
2. Optionally fetch delivery, fundamentals, sectors, and index data.
3. Run the analyses you need (`instrumentAnalysis`).
