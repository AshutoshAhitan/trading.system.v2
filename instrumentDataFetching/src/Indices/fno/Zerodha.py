import pandas, logging, re
from inspect import currentframe, getframeinfo

from datetime import datetime, timedelta

from .WeeklyStrikePrice import WeeklyStrikePrice as StrikePrice
from pandas import DataFrame
from .exception import DateNotProviedException, IntervalException
from ...utils.exception import DataFetchException

from kiteconnect import KiteConnect


class Zerodha(StrikePrice):

    def __init__(self, config: dict, dbConfigPath) -> None:
        super().__init__(config, dbConfigPath)
        self.config = config
        self.metaInfo = self.config['metaInfo']

    
    def instruments(self):
        kite = KiteConnect(api_key=self.config['zerodha.api.key'])
        kite.set_access_token(self.config["zerodha.access_token"])
        instruments = kite.instruments(exchange='NFO')

        df = pandas.DataFrame(instruments)
        df = df[(df['segment'] == 'NFO-OPT') & (df['name'] == 'NIFTY')]

        return df


    def fetchData(self, symbol: str, interval, period, exchange) -> DataFrame:

        if period is None:
            raise DateNotProviedException("period not provided")
        if interval is None:
            raise IntervalException("interval not valid")
            
        try :

            from_date, to_date = self.convert_period_to_dates(period)
            logging.debug(f'> from date: {from_date} to date: {to_date}')

            mappedInterval = self.map_interval(interval)
            logging.debug(f'> mapped interval: {mappedInterval}')

            kite = KiteConnect(api_key=self.config['zerodha.api.key'])
            kite.set_access_token(self.config["zerodha.access_token"])

            ltp = kite.ltp(f"{exchange}:{symbol}")
            instrument_token = ltp[f"{exchange}:{symbol}"]['instrument_token']
            logging.debug(f'> instrument token for {symbol} is {instrument_token}')

            data = kite.historical_data(instrument_token=instrument_token,
                                        from_date=from_date,
                                        to_date=to_date,
                                        interval=mappedInterval,
                                        continuous=False,
                                        oi=True)   

            data = pandas.DataFrame(data)
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

            # add symbol and timeframe
            # data = self._addSymbol(ohlcv=data, symbol=symbol)

            # add timeframe
            data = self._addTimeframe(ohlcv=data, interval=interval)

        except Exception as e:
            print(e)
            frameinfo = getframeinfo(currentframe())
            raise DataFetchException(f'{e.__str__} [{frameinfo.filename}:{frameinfo.lineno}]')

        
        logging.debug(f'> ohlcv data \n{data}')

        return data
    
    
    def _removeTimezone(self, ohlcv: DataFrame) -> DataFrame:
        ohlcv['Datetime'] = ohlcv['Datetime'].dt.tz_localize(None)
        return ohlcv

    def _addTimeframe(self, ohlcv: DataFrame, interval: str) -> DataFrame:

        ohlcv['Timeframe'] = interval
        return ohlcv

    def _addSymbol(self, ohlcv: DataFrame, symbol: str) -> DataFrame:

        ohlcv['Symbol'] = symbol
        return ohlcv

    def convert_period_to_dates(self, period: str) -> tuple:
        # Get the current date
        to_date = datetime.now()
    
        # Parse the period string
        match = re.match(r'(\d+)([a-zA-Z]+)', period)
        if not match:
            raise ValueError("Invalid period format. Use formats like '1mo', '1y', '15days'.")
    
        value, unit = int(match.group(1)), match.group(2).lower()
    
        # Calculate the from_date based on the unit
        if unit in ['d', 'day', 'days']:
            from_date = to_date - timedelta(days=value)
        elif unit in ['w', 'week', 'weeks', 'wk']:
            from_date = to_date - timedelta(weeks=value)
        elif unit in ['mo', 'month', 'months']:
            from_date = to_date - timedelta(days=value * 30)  # Approximation: 1 month = 30 days
        elif unit in ['y', 'year', 'years']:
            from_date = to_date - timedelta(days=value * 365)  # Approximation: 1 year = 365 days
        else:
            raise ValueError("Unsupported time unit. Use 'd', 'w', 'mo', or 'y'.")
    
        # Format the dates as strings
        from_date_str = from_date.strftime('%Y-%m-%d') + ' 00:00:00'
        to_date_str = to_date.strftime('%Y-%m-%d') + ' 23:59:59'
    
        return from_date_str, to_date_str

    def map_interval(self, input_interval: str) -> str:
        interval_mapping = {
            '1m': 'minute',
            '3m': '3minute',
            '5m': '5minute',
            '10m': '10minute',
            '15m': '15minute',
            '30m': '30minute',
            '60m': '60minute',
            '1d': 'day'
        }

        if input_interval not in interval_mapping:
            raise ValueError(f"Unsupported interval: {input_interval}. Supported intervals are: {list(interval_mapping.keys())}")

        return interval_mapping[input_interval]
