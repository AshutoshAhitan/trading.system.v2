import pandas, logging, re
from inspect import currentframe, getframeinfo

from datetime import datetime, timedelta

from .Liquidity import Liquidity
from pandas import DataFrame
from .exception import DateNotProviedException
from ..utils.exception import DataFetchException

from kiteconnect import KiteConnect


class Zerodha(Liquidity):

    def __init__(self, config: dict, dbConfigPath, symbolList) -> None:
        super().__init__(config, dbConfigPath, symbolList)
        self.config = config

    def fetchData(self, instrumentToken) -> DataFrame:

        liquidity = []
        data: DataFrame = self.__fetch(instrumentToken, period=self.config['ohlcv.period'])

        return data


    def __fetch(self, instrumentToken, period) -> DataFrame:

        if period is None:
            raise DateNotProviedException("period not provided")
            
        try :

            from_date, to_date = self.convert_period_to_dates(period)
            logging.debug(f'> from date: {from_date} to date: {to_date}')

            kite = KiteConnect(api_key=self.config['zerodha.api.key'])
            kite.set_access_token(self.config["zerodha.access_token"])

            data = kite.historical_data(instrument_token=instrumentToken,
                                        from_date=from_date,
                                        to_date=to_date,
                                        interval='day',
                                        continuous=False,
                                        oi=False)   

            data = pandas.DataFrame(data)
            logging.debug(f'> data recieved from zerodha \n{data}')

            # add symbol and timeframe
            data = self._addInstrumentToken(ohlcv=data, instrumentToken=instrumentToken)

            # add avg closing price
            data = self._addAvgClosingPrice(ohlcv=data)
            
            # add avg volume
            data = self._addAvgVolume(ohlcv=data)
            
            # add avg traded value
            data = self._addAvgTradedValue(ohlcv=data)

        except Exception as e:
            print(str(e) + f' [{instrumentToken}]')
            frameinfo = getframeinfo(currentframe())
            raise DataFetchException(f'{e.__str__} [{frameinfo.filename}:{frameinfo.lineno}]')

        
        liquidity = data[['instrumentToken', 'avgPrice', 'avgVolume', 'avgTradedValue']].drop_duplicates()
        logging.debug(f'> liquidity data \n{liquidity}')
        return liquidity
    
    def _addInstrumentToken(self, ohlcv: DataFrame, instrumentToken) -> DataFrame:
        ohlcv['instrumentToken'] = instrumentToken
        return ohlcv

    def _addAvgClosingPrice(self, ohlcv: DataFrame) -> DataFrame:
        ohlcv['avgPrice'] = ohlcv.close.mean().round(0)
        return ohlcv

    def _addAvgVolume(self, ohlcv: DataFrame) -> DataFrame:
        ohlcv['avgVolume'] = ohlcv.volume.mean().round(0)
        return ohlcv

    def _addAvgTradedValue(self, ohlcv: DataFrame) -> DataFrame:
        ohlcv['avgTradedValue'] = (ohlcv.close * ohlcv.volume).mean().round(0)
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
            raise ValueError("Unsupported time unit. Use 'm', 'd', 'w', 'mo', or 'y'.")
    
        # Format the dates as strings
        from_date_str = from_date.strftime('%Y-%m-%d') + ' 00:00:00'
        to_date_str = to_date.strftime('%Y-%m-%d') + ' 23:59:59'
    
        return from_date_str, to_date_str