import pandas, logging, re
from inspect import currentframe, getframeinfo

from datetime import datetime, timedelta

from .ohlcv import OHLCV
from pandas import DataFrame
from .exception import DateNotProviedException, IntervalException
from ..utils.exception import DataFetchException

from kiteconnect import KiteConnect


class Zerodha(OHLCV):

    def __init__(self, config: dict, dbConfigPath, symbolList) -> None:
        super().__init__(config, dbConfigPath, symbolList)
        self.config = config

        self.metaInfo = config['metaInfo']
        self.pennyStocks = config['pennyStocks']


    def fetchData(self, symbol: str) -> DataFrame:

        ohlcvDataList = []
        for aMetaInfo in self.metaInfo:
            if aMetaInfo['fetch']:
                data: DataFrame = self.__fetch(symbol, aMetaInfo['interval'], period=aMetaInfo['period'],
                                               day_range=aMetaInfo.get('day.range', None))
                ohlcvDataList.append(data)

        ohlcvDataList = pandas.concat(ohlcvDataList)
        logging.debug(ohlcvDataList)

        return ohlcvDataList


    def __fetch(self, symbol: str, interval, period, day_range) -> DataFrame:

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

            ltp = kite.ltp(f"NSE:{symbol}")
            instrument_token = ltp[f"NSE:{symbol}"]['instrument_token']
            logging.debug(f'> instrument token for {symbol} is {instrument_token}')

            data = kite.historical_data(instrument_token=instrument_token,
                                        from_date=from_date,
                                        to_date=to_date,
                                        interval=mappedInterval,
                                        continuous=False,
                                        oi=False)   

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

            # Convert 'Datetime' column back to datetime dtype
            data['Datetime'] = pandas.to_datetime(data['Datetime'], format='%Y-%m-%d %H:%M:%S')

            if interval == '1wk':
                logging.debug('> converting to weekly')
                data = self._convertToWeekly(data)

            # Filter data based on day.range in config if present
            if day_range is not None:
                data = self._filter_by_day_range(data, from_date, to_date, day_range)

            # add symbol and timeframe
            data = self._addSymbol(ohlcv=data, symbol=symbol)

            # add timeframe
            data = self._addTimeframe(ohlcv=data, interval=interval)

        except Exception as e:
            print(e)
            frameinfo = getframeinfo(currentframe())
            raise DataFetchException(f'{e.__str__} [{frameinfo.filename}:{frameinfo.lineno}]')

        
        logging.debug(f'> ohlcv data \n{data}')

        return data

    def _convertToWeekly(self, ohlcv: DataFrame) -> DataFrame:
        # Convert to datetime
        ohlcv["Datetime"] = pandas.to_datetime(ohlcv["Datetime"])

        ohlcv["Week"] = ohlcv["Datetime"].dt.to_period("W-FRI")

        weekly = ohlcv.groupby("Week").agg(
            Open=("Open", "first"),
            High=("High", "max"),
            Low=("Low", "min"),
            Close=("Close", "last"),
            Volume=("Volume", "sum")
        )

        # Convert period back to timestamp (week start date)
        weekly.index = weekly.index.start_time + timedelta(days=2)  # Move to Monday

        weekly.index.name = "Datetime"
        weekly = weekly.reset_index()

        return weekly
    
    
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
        elif unit in ['w', 'week', 'weeks']:
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
            '1d': 'day',
            '1wk': 'day',
        }

        if input_interval not in interval_mapping:
            raise ValueError(f"Unsupported interval: {input_interval}. Supported intervals are: {list(interval_mapping.keys())}")

        return interval_mapping[input_interval]

    def _filter_by_day_range(self, data: DataFrame, from_date: str, to_date: str, day_range: dict) -> DataFrame:
        """
        Filters the data DataFrame for each day in the date range, keeping only rows within the specified time window.
        """
        logging.debug(f'> filtering data between {from_date} and {to_date} with day range {day_range}')
        logging.debug(data)

        from_day = from_date.split()[0]
        to_day = to_date.split()[0]
        start_time = day_range['from']
        end_time = day_range['to']

        date_range = pandas.date_range(start=from_day, end=to_day, freq='D')
        filtered_data_list = []
        for single_date in date_range:
            day_str = single_date.strftime('%Y-%m-%d')
            start_dt = f"{day_str} {start_time}"
            end_dt = f"{day_str} {end_time}"

            day_filtered = data[(data['Datetime'] >= start_dt) & (data['Datetime'] <= end_dt)]
            logging.debug(f'> filtering data for date {day_str} between {start_dt} and {end_dt}, found {len(day_filtered)} records')
            filtered_data_list.append(day_filtered)

        if filtered_data_list:
            data = pandas.concat(filtered_data_list, ignore_index=True)
        else:
            data = data.iloc[0:0]  # empty DataFrame with same columns

        return data
