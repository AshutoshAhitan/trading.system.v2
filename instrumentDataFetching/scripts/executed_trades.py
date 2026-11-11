import logging, json
from kiteconnect import KiteConnect
import pandas as pd
from datetime import datetime, date, timedelta

logging.basicConfig(level=logging.INFO)

with open("../config/ohlcv.json") as f:
    config = json.load(f)

kite = KiteConnect(api_key=config['zerodha.api.key'])
kite.set_access_token(config["zerodha.access_token"])

# -------------------- DATE RANGE INPUT --------------------
def parse_date(prompt, default):
    while True:
        raw = input(f"{prompt} [{default}]: ").strip()
        if not raw:
            return default
        try:
            return datetime.strptime(raw, "%Y-%m-%d").date()
        except ValueError:
            print("  Invalid format. Use YYYY-MM-DD.")

today = date.today()
default_from = today - timedelta(days=30)
from_date = parse_date("From date (YYYY-MM-DD)", default_from)
to_date   = parse_date("To   date (YYYY-MM-DD)", today)

if from_date > to_date:
    print("Error: from_date must be <= to_date.")
    exit(1)
# ----------------------------------------------------------

# -------------------- FETCH TRADES --------------------
try:
    trades = kite.trades()
    if not trades:
        print("No trades found.")
    else:
        df = pd.DataFrame(trades)
        df['fill_timestamp'] = pd.to_datetime(df['fill_timestamp'])
        df = df.sort_values('fill_timestamp', ascending=True)

        # filter by date range
        df = df[
            (df['fill_timestamp'].dt.date >= from_date) &
            (df['fill_timestamp'].dt.date <= to_date)
        ]

        if df.empty:
            print(f"No trades found between {from_date} and {to_date}.")
        else:
            cols = [
                'trade_id', 'order_id', 'tradingsymbol', 'exchange',
                'transaction_type', 'product', 'order_type',
                'quantity', 'average_price', 'fill_timestamp'
            ]
            available_cols = [c for c in cols if c in df.columns]
            df = df[available_cols]

            print(f"\nExecuted Trades ({from_date} to {to_date}):")
            print(df.to_string(index=False))

            buys  = df[df['transaction_type'] == 'BUY']
            sells = df[df['transaction_type'] == 'SELL']
            print(f"\nTotal trades : {len(df)}")
            print(f"  BUY  trades: {len(buys)}")
            print(f"  SELL trades: {len(sells)}")

except Exception as e:
    logging.error(f"Error fetching trades: {e}")
# ------------------------------------------------------
