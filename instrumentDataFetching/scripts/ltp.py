import logging, json
from kiteconnect import KiteConnect
import pandas as pd
import numpy as np
from datetime import datetime

logging.basicConfig(level=logging.INFO)

# read json file
with open("../config/ohlcv.json") as f:
    config = json.load(f)

kite = KiteConnect(api_key=config['zerodha.api.key'])
kite.set_access_token(config["zerodha.access_token"])

# -----------------------------
# LTP Example
# -----------------------------

# Single instrument (NSE: INFY)
instruments = kite.instruments(exchange='BFO')
df = pd.DataFrame(instruments)
for row in df.itertuples():
    print(f"{row.tradingsymbol} ({row.exchange}): {row.last_price}")

instruments = kite.instruments(exchange='NFO')

df = pd.DataFrame(instruments)
df["expiry"] = pd.to_datetime(df["expiry"])
df["instrument_token"] = df["instrument_token"].astype("int64")
df["exchange_token"] = df["exchange_token"].astype(str)
df["last_price"] = pd.to_numeric(df["last_price"], errors="coerce")
df["strike"] = pd.to_numeric(df["strike"], errors="coerce")
df["tick_size"] = pd.to_numeric(df["tick_size"], errors="coerce")
df["lot_size"] = pd.to_numeric(df["lot_size"], errors="coerce", downcast="integer")

# print(df[(df.name == 'NIFTY') & (df.segment == 'NFO-OPT') & (df.instrument_type == 'CE')])
# print(df.expiry.unique())
# print("\nData types:\n", df.dtypes)

# --- Method to get nearest and next strike symbol ---
# def get_nifty_strike_and_next_symbol(ltp, df, date):
#     df_nifty_ce = df[(df.name == 'NIFTY') & (df.segment == 'NFO-OPT') & (df.instrument_type == 'CE')]
#     today = pd.Timestamp(datetime.now().date())
#     print('expiry : \n', df_nifty_ce.expiry.unique())
#     next_expiry = df_nifty_ce[df_nifty_ce.expiry >= date].expiry.min()
#     strikes = np.sort(df_nifty_ce[df_nifty_ce.expiry == next_expiry]['strike'].unique())
#     # Find nearest strike
#     nearest_strike = min(strikes, key=lambda x: abs(x - ltp)) if len(strikes) > 0 else round(ltp / 50) * 50
#     # Next strike is always nearest_strike + 150
#     next_strike = nearest_strike + 150
#     # Get tradingsymbols
#     row_nearest = df_nifty_ce[(df_nifty_ce.expiry == next_expiry) & (df_nifty_ce.strike == nearest_strike)].head(1)
#     row_next = df_nifty_ce[(df_nifty_ce.expiry == next_expiry) & (df_nifty_ce.strike == next_strike)].head(1)
#     symbol_nearest = row_nearest.iloc[0]['tradingsymbol'] if not row_nearest.empty else None
#     symbol_next = row_next.iloc[0]['tradingsymbol'] if not row_next.empty else None
#     return symbol_nearest, symbol_next

from datetime import datetime, timedelta
import pandas as pd
import numpy as np

def get_next_tuesday(given_date: pd.Timestamp):
    # weekday(): Monday=0 ... Sunday=6
    days_ahead = (1 - given_date.weekday()) % 7
    if days_ahead == 0:
        days_ahead = 7
    return given_date + timedelta(days=days_ahead)


def get_nifty_strike_and_next_symbol(ltp, df, given_date):
    """
    ltp        : NIFTY spot price
    df         : instruments dataframe
    given_date : date on which trade is taken (YYYY-MM-DD)
    """

    given_date = pd.Timestamp(given_date)

    # 1. Calculate next Tuesday expiry
    expiry_date = get_next_tuesday(given_date)
    print(f"Calculated next Tuesday expiry date: {expiry_date.date()}")

    # 2. Filter NIFTY CE options for that expiry
    df_nifty_ce = df[
        (df.name == 'NIFTY') &
        (df.segment == 'NFO-OPT') &
        (df.instrument_type == 'CE') &
        (df.expiry == expiry_date)
    ]

    # 3. Get available strikes
    strikes = np.sort(df_nifty_ce['strike'].unique())

    # 4. Find nearest strike
    if len(strikes) > 0:
        nearest_strike = min(strikes, key=lambda x: abs(x - ltp))
    else:
        nearest_strike = round(ltp / 50) * 50

    # 5. Next strike (+150)
    next_strike = nearest_strike + 150

    # 6. Fetch symbols
    row_nearest = df_nifty_ce[df_nifty_ce.strike == nearest_strike].head(1)
    row_next = df_nifty_ce[df_nifty_ce.strike == next_strike].head(1)

    symbol_nearest = row_nearest.iloc[0]['tradingsymbol'] if not row_nearest.empty else None
    symbol_next = row_next.iloc[0]['tradingsymbol'] if not row_next.empty else None

    return {
        "expiry": expiry_date.date(),
        "nearest_strike": nearest_strike,
        "nearest_symbol": symbol_nearest,
        "next_strike": next_strike,
        "next_symbol": symbol_next
    }


# Example usage for both strikes:
ltp_data = kite.ltp("NSE:NIFTY 50")
print("LTP:", ltp_data["NSE:NIFTY 50"]["last_price"])
ltp_nifty = ltp_data["NSE:NIFTY 50"]["last_price"]
res = get_nifty_strike_and_next_symbol(ltp_nifty, df, '2025-12-17')
print(res)
# print(f"nifty ltp : {ltp_nifty}, Nearest Strike Symbol: {symbol_nearest}, Next Strike Symbol: {symbol_next}")

# instrument_token = df[df.tradingsymbol == symbol_next]['instrument_token'].values[0]
# print(f"Instrument token for {symbol_next} is {instrument_token}")

# data = kite.historical_data(instrument_token, from_date="2025-12-09 09:15:00", to_date="2025-12-09 09:20:00", interval="minute")
# print("Historical data sample:\n", pd.DataFrame(data).head())

