import numpy as np, pandas as pd
import logging, json
from kiteconnect import KiteConnect
import numpy as np
import talib

logging.basicConfig(level=logging.INFO)


import pandas as pd

def heikin_ashi(df):
    """
    Calculate Heikin-Ashi candles
    df must have columns: ['open', 'high', 'low', 'close']
    """
    ha = df.copy()

    # Heikin-Ashi Close
    ha['ha_close'] = (df['open'] + df['high'] + df['low'] + df['close']) / 4

    # Heikin-Ashi Open
    ha['ha_open'] = 0.0
    ha.loc[ha.index[0], 'ha_open'] = (df['open'].iloc[0] + df['close'].iloc[0]) / 2

    for i in range(1, len(df)):
        ha.loc[ha.index[i], 'ha_open'] = (
            ha.loc[ha.index[i-1], 'ha_open'] +
            ha.loc[ha.index[i-1], 'ha_close']
        ) / 2

    # Heikin-Ashi High & Low
    ha['ha_high'] = ha[['ha_open', 'ha_close']].join(df['high']).max(axis=1)
    ha['ha_low']  = ha[['ha_open', 'ha_close']].join(df['low']).min(axis=1)

    ha['ha_close'] = ha['ha_close'].round(2)
    ha['ha_open'] = ha['ha_open'].round(2)
    ha['ha_high'] = ha['ha_high'].round(2)
    ha['ha_low'] = ha['ha_low'].round(2)

    df['ha_open'] = ha['ha_open']
    df['ha_high'] = ha['ha_high']
    df['ha_low']  = ha['ha_low']
    df['ha_close']= ha['ha_close']

    return df



# read json file
with open("../config/ohlcv.json") as f:
    config = json.load(f)

kite = KiteConnect(api_key=config['zerodha.api.key'])
kite.set_access_token(config["zerodha.access_token"])

# -----------------------------
# LTP Example
# -----------------------------

# instruments = kite.instruments(exchange='NSE')
# instruments = pd.DataFrame(instruments)
# instruments = instruments[instruments['tradingsymbol']=='NIFTY 50']
# print(instruments)

# Single instrument (NSE: INFY)
# ltp_data = kite.ltp("NSE:AXISBANK")
# instrument_token = ltp_data["NSE:AXISBANK"]["instrument_token"]

ltp_data = kite.ltp("NSE:NIFTY 50")
print("LTP:", ltp_data["NSE:NIFTY 50"]["last_price"])
instrument_token = ltp_data["NSE:NIFTY 50"]["instrument_token"]


historical_data = kite.historical_data(instrument_token, 
                                      from_date="2025-12-15 09:15:00", 
                                      to_date="2025-12-15 15:29:00", 
                                      interval="minute")
df = pd.DataFrame(historical_data)
df['date'] = df['date'].dt.tz_localize(None)

df['adx'] = talib.ADX(df['high'], df['low'], df['close'], timeperiod=10)
df['adx'] = df['adx'].round(0)


df = heikin_ashi(df)

df['ha_adx'] = talib.ADX(df['ha_high'], df['ha_low'], df['ha_close'], timeperiod=10)
df['ha_adx'] = df['ha_adx'].round(0)

df["+di"] = talib.PLUS_DI(df["ha_high"], df["ha_low"], df["ha_close"], 10)
df["-di"] = talib.MINUS_DI(df["ha_high"], df["ha_low"], df["ha_close"], 10)

print(df[['date',  'close', 'adx']].tail(10))
print(df[['date',  'ha_close', 'ha_adx']].tail(10))


