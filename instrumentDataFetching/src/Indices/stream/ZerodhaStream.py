from collections import defaultdict
import time
from kiteconnect import KiteTicker
from multiprocessing import Queue, Process
import logging, json
from pandas import DataFrame
import pandas as pd
from kiteconnect import KiteConnect
from ...Database.DatabaseFactory import DatabaseFactory
import signal, os

# -------------- SIGNAL HANDLER ---------------- #
def send_sigusr2(pid):
    os.kill(pid, signal.SIGUSR2)

# ---------------- STATE FACTORY ---------------- #
def create_state(dataQueue, instrument_tokens):
    return {
        "candles": defaultdict(dict),
        "last_minute_seen": {},
        "dataQueue": dataQueue,
        "instrument_tokens_count": len(instrument_tokens)
    }

# ---------------- UTILS ---------------- #
def floor_minute(ts):
    return ts.replace(second=0, microsecond=0)

def floor_to_3min(ts):
    floored_minute = ts.minute - (ts.minute % 3)
    return ts.replace(minute=floored_minute, second=0, microsecond=0)


# ---------------- CANDLE LOGIC ---------------- #
def emit_and_delete(state, token, minute, instrument_token_count):
    key = (token, minute)
    candle = state["candles"].get(key)
    if candle:
        on_candle_close(state, candle)
        del state["candles"][key]

def on_candle_close(state, candle):
    state["dataQueue"].put(candle)
    print(f"CLOSED: {candle} at {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}")


# ---------------- WS CALLBACKS ---------------- #
def on_ticks_factory(state, token_symbol_map):
    def on_ticks(ws, ticks):
        for tick in ticks:
            # print(tick)
            token = tick["instrument_token"]
            ltp = tick["last_price"]
            ts = tick["exchange_timestamp"]

            # minute = floor_minute(ts)
            minute = floor_to_3min(ts)
            key = (token, minute)

            if token in state["last_minute_seen"] and minute > state["last_minute_seen"][token]:
                emit_and_delete(state, token, state["last_minute_seen"][token], instrument_token_count=state["instrument_tokens_count"])

            volume = tick.get("volume", 0)
            oi = tick.get("oi", 0)
            if key not in state["candles"]:
                state["candles"][key] = {
                    "Symbol": token_symbol_map.get(token)[0],
                    "Timeframe": "3m",
                    "Datetime": minute,
                    "Open": ltp,
                    "High": ltp,
                    "Low": ltp,
                    "Close": ltp,
                    "Volume": volume,
                    "oi": oi,
                    "strikePrice": token_symbol_map.get(token)[1],
                    "expiry": token_symbol_map.get(token)[2],
                    "instrumentType": token_symbol_map.get(token)[3]
                }
            else:
                c = state["candles"][key]
                c["High"] = max(c["High"], ltp)
                c["Low"] = min(c["Low"], ltp)
                c["Close"] = ltp
                c["Volume"] += volume
                c["oi"] = oi  # update OI with latest value
            

            state["last_minute_seen"][token] = minute

    return on_ticks



def on_connect_factory(instrument_tokens):
    def on_connect(ws, response):
        ws.subscribe(instrument_tokens)
        ws.set_mode(ws.MODE_FULL, instrument_tokens)
    return on_connect

def on_close(ws, code, reason):
    print(f"WebSocket closed: {code} - {reason}")

def on_error(ws, code, reason):
    print(f"WebSocket error: {code} - {reason}")

# ---------------- ENTRY POINT ---------------- #
def _stream(api_key, access_token, instrument_tokens, token_symbol_map, dataQueue):
    state = create_state(dataQueue, instrument_tokens)

    kws = KiteTicker(api_key, access_token)
    kws.on_connect = on_connect_factory(instrument_tokens)
    kws.on_ticks = on_ticks_factory(state, token_symbol_map)
    kws.on_close = on_close
    kws.on_error = on_error

    kws.connect(threaded=False)


def stream(instrument_token, token_symbol_map ,streamConfigPath, ohlcvConfigPath, dbConfigPath, pid):

    with open(ohlcvConfigPath) as f:
        ohlcvConfig = json.load(f)

    with open(streamConfigPath) as f:
        config = json.load(f)

    kite = KiteConnect(api_key=ohlcvConfig["zerodha.api.key"])
    kite.set_access_token(ohlcvConfig["zerodha.access_token"])

    dataQ = Queue()

    logging.info(f"Starting stream for token {instrument_token}...")

    p1 = Process(target=_stream, args=(
        ohlcvConfig["zerodha.api.key"],
        ohlcvConfig["zerodha.access_token"],
        instrument_token,
        token_symbol_map,
        dataQ
    ))
    p1.start()

    database = DatabaseFactory.create(dbConfigPath)

    count = 0; instrument_token_count = len(instrument_token)
    while True:
        tick = dataQ.get()

        ohlcv = DataFrame()
        ohlcv = pd.concat([ohlcv, pd.DataFrame([tick])], ignore_index=True)

        database.saveRecords(
            config['dest.table'],
			config['dest.table.primary.keys'],
			ohlcv)

        count += 1
        if count == instrument_token_count:
            count = 0
            now = pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
            logging.info(f"{now} : fetched all tokens for minute {tick['Datetime']}. Waiting for next minute...")
            send_sigusr2(pid)
    
    p1.join()


def test_stream(instrument_token, token_symbol_map ,streamConfigPath, ohlcvConfigPath, dbConfigPath, pid):

    with open(ohlcvConfigPath) as f:
        ohlcvConfig = json.load(f)

    with open(streamConfigPath) as f:
        config = json.load(f)

    kite = KiteConnect(api_key=ohlcvConfig["zerodha.api.key"])
    kite.set_access_token(ohlcvConfig["zerodha.access_token"])

    logging.info(f"fetching ohlcv for token {instrument_token}...")

    ohlcv = DataFrame()
    for token in instrument_token:
        logging.info(f"fetching ohlcv for token {token} : symbol {token_symbol_map[token]} ...")
        data = kite.historical_data(instrument_token=token,
                                    from_date='2026-05-20 10:30:00',
                                    to_date='2026-05-20 11:00:00',
                                    interval='minute',
                                    oi=True,
                                    continuous=False)   

        data = pd.DataFrame(data)
        data = data.rename(columns={
            'date': 'Datetime',
            'open': 'Open',
            'low': 'Low',
            'high': 'High',
            'close': 'Close',
            'volume': 'Volume'
        })

        # Remove timezone info
        data['Datetime'] = data['Datetime'].dt.tz_localize(None)

        # Convert to string with desired format, e.g., 'YYYY-MM-DD HH:MM:SS'
        data['Datetime'] = data['Datetime'].dt.strftime('%Y-%m-%d %H:%M:%S')

        # Convert 'Datetime' column back to datetime dtype
        data['Datetime'] = pd.to_datetime(data['Datetime'], format='%Y-%m-%d %H:%M:%S')

        # add timeframe and symbol columns
        data['Timeframe'] = '3m'
        data['Symbol'] = token_symbol_map[token][0]

        data['strike'] = token_symbol_map[token][0]
        data['expiry'] = token_symbol_map[token][2]
        data['instrumentType'] = token_symbol_map[token][3]

        logging.info(f'> fetched ohlcv data for token {token}:\n {data}')

        ohlcv = pd.concat([ohlcv, data], ignore_index=True)

    print(ohlcv)
    database = DatabaseFactory.create(dbConfigPath)

    # Group by Datetime and save all symbols for each time one after another
    for dt, group in ohlcv.groupby('Datetime'):
        logging.info(f"> saving records for time {dt} to database:\n{group}")
        database.saveRecords(config['dest.table'], config['dest.table.primary.keys'], group)
        send_sigusr2(pid)
        time.sleep(3)
