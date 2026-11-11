import logging, json, time
from kiteconnect import KiteConnect
import pandas as pd

logging.basicConfig(level=logging.INFO)

def get_token_from_tradingsymbol(instruments_df, tradingsymbol):
    """
    Fetch the instrument token for a given trading symbol.
    :param instruments_df: DataFrame containing instrument data (must have 'tradingsymbol' and 'instrument_token' columns)
    :param tradingsymbol: The trading symbol to look up
    :return: instrument_token or None if not found
    """
    row = instruments_df.loc[instruments_df['tradingsymbol'] == tradingsymbol]
    if not row.empty:
        return row.iloc[0]['instrument_token']
    return None

# ----------------------------------------------------
# Fetch ATM strike price OHLCV for NIFTY option
def fetch_atm_strike_ohlcv():
    # Get NIFTY LTP
    niftyLTP = kite.ltp('NSE:NIFTY 50')
    ltp = niftyLTP['NSE:NIFTY 50']['last_price']
    print(f"NIFTY 50 LTP: {ltp}")
    # Round to nearest 50 for ATM strike
    atm_strike = round(ltp / 50) * 50

    # Get all NIFTY option instruments
    instruments = kite.instruments(exchange='NFO')
    df = pd.DataFrame(instruments)
    df = df[(df['segment'] == 'NFO-OPT') & (df['name'] == 'NIFTY')]
    # Get next expiry
    next_expiry = df['expiry'].sort_values().unique()[0]
    df = df[pd.to_datetime(df['expiry']) == pd.to_datetime(next_expiry)]
    # Find ATM strike row
    row = df[df['strike'] == atm_strike]
    if row.empty:
        raise Exception(f"No instrument found for ATM strike {atm_strike}")
    instrument_token = row.iloc[0]['instrument_token']
    tradingsymbol = row.iloc[0]['tradingsymbol']

    strikePrice = 24750
    start_datetime = '2026-03-06 11:22:00'
    end_datetime = '2026-03-06 11:42:00'

    # Fetch OHLCV for ATM strike
    instrument_token = get_token_from_tradingsymbol(df, f'NIFTY26310{strikePrice}PE')  # Just to verify the function works
    ohlcv_pe = kite.historical_data(instrument_token, interval='minute', from_date=start_datetime, to_date=end_datetime, oi=True)
    ohlcv_pe = pd.DataFrame(ohlcv_pe)
    if not ohlcv_pe.empty:
        ohlcv_pe['date'] = ohlcv_pe['date'].dt.tz_localize(None)
    print(f"ATM Strike: {atm_strike}, Symbol: {tradingsymbol}")
    ohlcv_pe['oi_change'] = ohlcv_pe['oi'].diff()
    # Replace 0 with previous value in oi_change
    import numpy as np
    ohlcv_pe['oi_change'] = ohlcv_pe['oi_change'].replace(0, np.nan).ffill()
    ohlcv_pe['volume_change'] = ohlcv_pe['volume'].diff()
    print(ohlcv_pe.tail(100))

    # Fetch OHLCV for ATM strike
    instrument_token = get_token_from_tradingsymbol(df, f'NIFTY26310{strikePrice}CE')  # Just to verify the function works
    ohlcv_ce = kite.historical_data(instrument_token, interval='minute', from_date=start_datetime, to_date=end_datetime, oi=True)
    ohlcv_ce = pd.DataFrame(ohlcv_ce)
    if not ohlcv_ce.empty:
        ohlcv_ce['date'] = ohlcv_ce['date'].dt.tz_localize(None)
    print(f"ATM Strike: {atm_strike}, Symbol: {tradingsymbol}")
    ohlcv_ce['oi_change'] = ohlcv_ce['oi'].diff()
    # Replace 0 with previous value in oi_change
    ohlcv_ce['oi_change'] = ohlcv_ce['oi_change'].replace(0, np.nan).ffill()
    ohlcv_ce['pe_to_ce_oi_change'] = ohlcv_pe['oi_change'] / ohlcv_ce['oi_change']
    print(ohlcv_ce.tail(100))

    ohlcv = pd.DataFrame()
    ohlcv['date'] = ohlcv_pe['date']
    ohlcv['pe_oi_change'] = ohlcv_pe['oi_change']
    ohlcv['ce_oi_change'] = ohlcv_ce['oi_change']
    ohlcv['pe_to_ce_oi_change'] = ohlcv_pe['oi_change'] / ohlcv_ce['oi_change']

    # ohlcv['pe_volume'] = ohlcv_pe['volume']
    # ohlcv['ce_volume'] = ohlcv_ce['volume']
    # ohlcv['pe_to_ce_volume_change'] = ohlcv['pe_volume'] / ohlcv['ce_volume']

    print(ohlcv)


    return ohlcv_ce

# ----------------------------------------------------
# read json file
with open("../config/ohlcv.json") as f:
    config = json.load(f)

kite = KiteConnect(api_key=config['zerodha.api.key'])
kite.set_access_token(config["zerodha.access_token"])
# ----------------------------------------------------


# ----------------------------------------------------
niftyLTP = kite.ltp('NSE:NIFTY 50')
print(niftyLTP)
niftyInstrumentToken = niftyLTP['NSE:NIFTY 50']['instrument_token']

while True:
    nifty50_ohlcv = kite.historical_data(niftyInstrumentToken, interval='minute', from_date='2026-01-13',
                                         to_date='2026-01-13')
    nifty50_ohlcv = pd.DataFrame(nifty50_ohlcv)

    # remove timezone from date field
    nifty50_ohlcv['date'] = nifty50_ohlcv['date'].dt.tz_localize(None)

    print(nifty50_ohlcv.tail(1))
    time.sleep(0.50)
    break;
# ----------------------------------------------------

# Example usage:
fetch_atm_strike_ohlcv()