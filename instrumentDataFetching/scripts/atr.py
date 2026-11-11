import pandas as pd
import numpy as np
import mplfinance as mpf
import logging, json
from kiteconnect import KiteConnect
import pandas as pd
import talib
import numpy as np


logging.basicConfig(level=logging.INFO)

# Plot candlestick chart with ATR
def plot_candlestick_with_atr(df):
    apds = [
        mpf.make_addplot(df['trailing_stop_loss'], color='red', width=1.5, ylabel='Trailing Stoploss'),
    ]
    mpf.plot(
        df,
        type='candle',
        style='yahoo',
        addplot=apds,
        volume=True,
        figsize=(12,8),
        title='Candlestick with ATR & Trailing Stoploss'
    )


def trailing_stop_loss(df, atr_multiplier=3):
    df['trailing_stop_loss'] = df['Low'] - (atr_multiplier * df['atr'])
    return df


# ----------------------------------------------------
# read json file
with open("../config/ohlcv.json") as f:
    config = json.load(f)

kite = KiteConnect(api_key=config['zerodha.api.key'])
kite.set_access_token(config["zerodha.access_token"])
# ----------------------------------------------------


# ----------------------------------------------------
niftyLTP = kite.ltp('NFO:NIFTY2621025750CE')
print(niftyLTP)
niftyInstrumentToken = niftyLTP['NFO:NIFTY2621025750CE']['instrument_token']

df = kite.historical_data(niftyInstrumentToken, interval='minute', from_date='2026-02-06',
                                        to_date='2026-02-06')
df = pd.DataFrame(df)

# remove timezone from date field
df['date'] = df['date'].dt.tz_localize(None)
# ----------------------------------------------------


# ----------------------------------------------------
df.rename(columns={'date': 'Date', 'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close', 'volume': 'Volume'}, inplace=True)
# Sample data (OHLCV DataFrame)
df['Date'] = pd.to_datetime(df['Date'])
df.set_index('Date', inplace=True)

high = np.array(df['High'], dtype=float)
low = np.array(df['Low'], dtype=float)
close = np.array(df['Close'], dtype=float)

period = 14
atr = talib.ATR(high, low, close, timeperiod=period)
df['atr'] = atr

trailing_stop_loss(df, atr_multiplier=0.5)

print(df)
plot_candlestick_with_atr(df[(df.index >= '2026-02-06 14:25:00') & (df.index <= '2026-02-06 15:00:00')])
# ----------------------------------------------------

