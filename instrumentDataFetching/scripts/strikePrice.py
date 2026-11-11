import logging, json
from kiteconnect import KiteConnect
import pandas as pd
import numpy as np
from datetime import datetime

logging.basicConfig(level=logging.INFO)

# ----------------------------------------------------
# read json file
with open("../config/indices.json") as f:
    config = json.load(f)

kite = KiteConnect(api_key=config['zerodha.api.key'])
kite.set_access_token(config["zerodha.access_token"])
# ----------------------------------------------------


# ----------------------------------------------------
niftyLTP = kite.ltp('NFO:NIFTY26JUNFUT')
niftyInstrumentToken = niftyLTP['NFO:NIFTY26JUNFUT']['instrument_token']
print(niftyLTP)
print(niftyInstrumentToken)


nifty50_ohlcv = kite.historical_data(niftyInstrumentToken, interval='3minute', from_date='2026-06-12',
                                     to_date='2026-06-12')
nifty50_ohlcv = pd.DataFrame(nifty50_ohlcv)
# remove timezone from date field
nifty50_ohlcv['date'] = nifty50_ohlcv['date'].dt.tz_localize(None)
print(nifty50_ohlcv)
# ----------------------------------------------------


# ----------------------------------------------------
instruments = kite.instruments(exchange='NFO')

df = pd.DataFrame(instruments)
df = df[(df['segment'] == 'NFO-OPT') & (df['name'] == 'NIFTY') & (df['instrument_type'] == 'CE')]
nextWeeklyExpiry = df['expiry'].sort_values().unique()[0]
print("next Weekly Expiry Date: ", nextWeeklyExpiry)

df = df[pd.to_datetime(df['expiry']) == pd.to_datetime(nextWeeklyExpiry)]
df = df.sort_values(by='strike', ascending=True)
print(df[['instrument_token', 'tradingsymbol', 'expiry', 'strike']])
len(df)
# ----------------------------------------------------


# ----------------------------------------------------
def __strikeSymbol(instruments, strikePrice):
    row = instruments[instruments['strike'] == strikePrice]
    if not row.empty:
        return row.iloc[0]['tradingsymbol']
    return None


closeValues = nifty50_ohlcv['close'].unique()
closeValues = closeValues.round(0)
print("Unique close values: ", len(closeValues))
for ltp in closeValues:
    nearest_strike = round(ltp / 50) * 50
    strikes = [nearest_strike, nearest_strike + 50, nearest_strike + 2*50, nearest_strike + 3*50]
    strikeSymbol = [__strikeSymbol(df, strike) for strike in strikes]
    print(f"LTP: {ltp}, Nearest Strike: {nearest_strike}")
    print(f'strikes : {strikes}; symbols: {strikeSymbol}')
    if None in strikeSymbol:
        raise Exception('None found for strike symbol')

    break

ltp = kite.ltp('NFO:NIFTY25D2325950CE')
print(ltp)

