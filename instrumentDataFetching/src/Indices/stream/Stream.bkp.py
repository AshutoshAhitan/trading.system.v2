import json, time
import pandas as pd
from kiteconnect import KiteConnect
from multiprocessing import Process

from . import ZerodhaStream
import logging
from ...Database.DatabaseFactory import DatabaseFactory

def get_nifty_option_tokens(kite, ltp, range=400):

    instruments = kite.instruments(exchange='NFO')

    df = pd.DataFrame(instruments)

    df = df[(df['segment'] == 'NFO-OPT') & (df['name'] == 'NIFTY') & (df['instrument_type'].isin(['CE', 'PE']))]
    next_expiry = df['expiry'].sort_values().unique()[0]

    df = df[pd.to_datetime(df['expiry']) == pd.to_datetime(next_expiry)]
    df = df.sort_values(by=['strike', 'instrument_type'], ascending=[True, True])

    upper_bound = ltp + range
    lower_bound = ltp - range
    tokens_df = df[(df['strike'] >= lower_bound) & (df['strike'] <= upper_bound)][['instrument_token', 'tradingsymbol', 'strike']].copy()

    logging.info(f"ltp : {ltp}; range: {range}; upper_bound: {upper_bound}; lower_bound: {lower_bound}; expiry: {next_expiry}")
    logging.info(f'strikes : {tokens_df['strike'].unique()}')

    # Map of token to symbol
    token_symbol_map = dict(
        zip(
            df['instrument_token'],
            zip(df['tradingsymbol'], df['strike'], df['expiry'], df['instrument_type'])
        )
    )

    return tokens_df, token_symbol_map


def _get_instrument_token(kite, symbol):
    ltp_data = kite.ltp(f"NFO:{symbol}")
    print(f"ltp_data : {ltp_data}")
    instrument_token = ltp_data[f"NFO:{symbol}"]['instrument_token']
    ltp = ltp_data[f"NFO:{symbol}"]['last_price']
    return instrument_token, ltp


def _fetch_histroical_data(kite, instrument_token, token_symbol_mapping, period, interval):
    to_date = pd.Timestamp.now().replace(second=0, microsecond=0)
    from_date = to_date - pd.Timedelta(hours=period)

    try:
        historical_data = kite.historical_data(
            instrument_token,
            from_date,
            to_date,
            interval,
            oi=True
        )
    except Exception as e:
        logging.error(f"Error fetching historical data for token {instrument_token}: {e}")
    
    logging.info(f"Fetched historical data for token {instrument_token} from {from_date} to {to_date} with interval {interval}")

    ohlcv = pd.DataFrame(historical_data)
    ohlcv.rename(columns={
        'date': 'Datetime',
        'open': 'Open',
        'high': 'High', 
        'low': 'Low',
        'close': 'Close',
        'volume': 'Volume'
    }, inplace=True)

    # remove time zone info from Datetime
    ohlcv['Datetime'] = ohlcv['Datetime'].dt.tz_localize(None)

    # add timeframe column
    ohlcv['Timeframe'] = "3m"

    # add symbol column
    ohlcv['Symbol'] = token_symbol_mapping[instrument_token][0]

    ohlcv = ohlcv.sort_values("Datetime", ascending=True)
    
    return ohlcv


def _fetch_historical_data_for_tokens(kite, config, database, tokens, token_symbol_mapping, period, interval):

    for token in tokens:
        ohlcv = _fetch_histroical_data(kite, token, token_symbol_mapping, period, interval)
        ohlcv['strikePrice'] = token_symbol_mapping[token][1]
        ohlcv['expiry'] = token_symbol_mapping[token][2]
        ohlcv['instrumentType'] = token_symbol_mapping[token][3]
        time.sleep(0.100)  # to avoid hitting rate limits

        database.saveRecords(
            config['dest.table'],
            config['dest.table.primary.keys'],
            ohlcv)


def _pid(pidFilePath):
    try:
        with open(pidFilePath, 'r') as f:
            pid = int(f.read().strip())
            return pid
    except Exception as e:
        logging.error(f"Error reading PID file: {e}")
        return None


def __fetch_historical_data_for_tokens(kite, streamConfig, database, tokens, token_symbol_map, 
                                       period=1, interval='minute'):
    while True:
        now = pd.Timestamp.now()
        total_seconds = now.minute * 60 + now.second + now.microsecond / 1e6

        # Next 3-minute boundary (in seconds) + 45
        cycle = 3 * 60  # 180 seconds
        target_offset = 45  # :45 of every 3rd minute

        next_target = (total_seconds // cycle + 1) * cycle + target_offset
        sleep_seconds = next_target - total_seconds

        logging.info(f'Sleeping for {sleep_seconds:.2f}s until next fetch cycle [historical data]...')
        time.sleep(sleep_seconds)

        now = pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        logging.info(f"{now} : Fetching historical data for all tokens...")
        _fetch_historical_data_for_tokens(
            kite,
            streamConfig,
            database,
            tokens,
            token_symbol_map,
            period=period,
            interval=interval,
        )
        now = pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        logging.info(f"{now} : Historical data fetch complete. Waiting for next fetch cycle...")


def stream(streamConfigPath, ohlcvConfigPath, dbConfigPath, pidFilePath):

    with open(ohlcvConfigPath) as f:
        ohlcvConfig = json.load(f)

    with open(streamConfigPath) as f:
        streamConfig = json.load(f)

    kite = KiteConnect(api_key=ohlcvConfig['zerodha.api.key'])
    kite.set_access_token(ohlcvConfig['zerodha.access_token'])

    instrument_token, ltp = _get_instrument_token(kite, streamConfig['stream.symbol'])

    tokens_df, token_symbol_map = get_nifty_option_tokens(kite, ltp)
    tokens = tokens_df['instrument_token'].tolist()
    token_symbol_map[instrument_token] = (streamConfig['stream.symbol'], 0, '2026-01-01', '')

    tokens.append(instrument_token)

    print(f"Found {len(tokens)} Nifty option (CE+PE) tokens for next expiry. Spawning streams...")

    p = Process(
        target=ZerodhaStream.stream,
        args=(
            tokens,
            token_symbol_map,
            streamConfigPath,
            ohlcvConfigPath,
            dbConfigPath,
            _pid(pidFilePath)
        )
    )
    p.start()

    database = DatabaseFactory.create(dbConfigPath)
    __fetch_historical_data_for_tokens(kite, streamConfig, database, tokens, token_symbol_map,
                                           period=1, interval='3minute')


    p.join()


def test_stream(streamConfigPath, ohlcvConfigPath, dbConfigPath, pidFilePath):

    with open(ohlcvConfigPath) as f:
        ohlcvConfig = json.load(f)

    with open(streamConfigPath) as f:
        streamConfig = json.load(f)

    kite = KiteConnect(api_key=ohlcvConfig['zerodha.api.key'])
    kite.set_access_token(ohlcvConfig['zerodha.access_token'])

    instrument_token, ltp = _get_instrument_token(kite, streamConfig['stream.symbol'])

    tokens_df, token_symbol_map = get_nifty_option_tokens(kite, ltp)
    tokens = tokens_df['instrument_token'].tolist()
    token_symbol_map[instrument_token] = streamConfig['stream.symbol']

    tokens.append(instrument_token)

    print(f"Found {len(tokens)} Nifty option (CE+PE) tokens for next expiry. Spawning streams...")

    p = Process(
        target=ZerodhaStream.test_stream,
        args=(
            tokens,
            token_symbol_map,
            streamConfigPath,
            ohlcvConfigPath,
            dbConfigPath,
            _pid(pidFilePath)
        )
    )
    p.start()
    p.join()
