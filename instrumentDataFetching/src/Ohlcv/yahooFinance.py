import yfinance as yf
import pendulum as pn
import pandas, logging
from inspect import currentframe, getframeinfo

from .ohlcv import OHLCV
from pandas import DataFrame
from .exception import DateNotProviedException, IntervalException
from ..utils.exception import PENNYSTOCKEXCEPTION, VolumeThresholdException, DataFetchException


class YahooFinance(OHLCV):

    def __init__(self, config: dict, dbConfigPath, symbolList) -> None:
        super().__init__(config, dbConfigPath, symbolList)

        self.metaInfo = config['metaInfo']
        self.pennyStocks = config['pennyStocks']
        self.config = config


    def fetchData(self, symbol: str) -> DataFrame:

        ohlcvDataList = []
        for aMetaInfo in self.metaInfo:
            data: DataFrame = self.__fetch(symbol, aMetaInfo['interval'], period=aMetaInfo['period'])
            ohlcvDataList.append(data)

        ohlcvDataList = pandas.concat(ohlcvDataList)
        logging.debug(ohlcvDataList)

        return ohlcvDataList


    def __fetch(self, symbol: str, interval, period) -> DataFrame:

        ticker = yf.Ticker(symbol+'.NS')
        if period is None:
            raise DateNotProviedException("period not provided")
        if interval is None:
            raise IntervalException("interval not valid")
            
        try :
            data = ticker.history(period=period, interval=interval)
            logging.debug(f'> data recieved from yfinance \n{data}')
        except Exception as e:
            frameinfo = getframeinfo(currentframe())
            raise DataFetchException(f'{e.__str__} [{frameinfo.filename}:{frameinfo.lineno}]')

        data = self._removeTimezone(ohlcvDataFrame=data)
        data = self._dropnaRecord(ohlcvDataFrame=data)
        data = self._dropRecordBasedOnDate(ohlcvDataFrame=data, interval=interval)
        data = self._addSymbol(ohlcvDataFrame=data, symbol=symbol)
        data = self._addTimeframe(ohlcvDataFrame=data, interval=interval)
        data.fillna(0)


        data = data.reset_index()
        data.rename(columns = {'Date':'Datetime'}, inplace = True) 
        logging.debug(f'> data after post processing \n{data}')

        return data
    
    
    def _removeTimezone(self, ohlcvDataFrame: DataFrame) -> DataFrame:
        ohlcvDataFrame.index = ohlcvDataFrame.index.tz_localize(None)
        return ohlcvDataFrame

    def _removeMultiLevelIndex(self, ohlcvDataFrame: DataFrame, symbol) -> DataFrame:
        ohlcv = pandas.DataFrame ({
            'Open' : ohlcvDataFrame.Open[symbol],
            'High' : ohlcvDataFrame.High[symbol],
            'Low' : ohlcvDataFrame.Low[symbol],
            'Close' : ohlcvDataFrame.Close[symbol],
            'Volume' : ohlcvDataFrame.Volume[symbol],
        })
        return ohlcv


    def _addTimeframe(self, ohlcvDataFrame: DataFrame, interval: str) -> DataFrame:

        ohlcvDataFrame['Timeframe'] = interval
        return ohlcvDataFrame


    def _addSymbol(self, ohlcvDataFrame: DataFrame, symbol: str) -> DataFrame:

        ohlcvDataFrame['Symbol'] = symbol
        return ohlcvDataFrame

    

    def _dropRecordBasedOnDate(self, ohlcvDataFrame: DataFrame, interval: str):

        now = pn.now()

        if interval == '1wk':
            startDate = now._start_of_week().date()
        elif interval == '1mo':
            startDate = now._start_of_month().date()
        else:
            return ohlcvDataFrame

        lastRecordDate  = ohlcvDataFrame.iloc[-1].name
        lastRecord      = ohlcvDataFrame.iloc[-1]
        if lastRecordDate != startDate:
            previousRecord = ohlcvDataFrame.iloc[-2]
            previousRecordDate = ohlcvDataFrame.iloc[-2].name

            ohlcvDataFrame.at[previousRecordDate, 'High']   = max(lastRecord.High, previousRecord.High)
            ohlcvDataFrame.at[previousRecordDate, 'Low']    = min(lastRecord.Low, previousRecord.Low)
            ohlcvDataFrame.at[previousRecordDate, 'Close']  = lastRecord.Close

            ohlcvDataFrame = ohlcvDataFrame.drop(lastRecordDate)

        return ohlcvDataFrame

    


    def _dropnaRecord(self, ohlcvDataFrame: DataFrame) -> DataFrame:

        isnaRecord = ohlcvDataFrame[ohlcvDataFrame['Close'].isna() == True]
        ohlcvDataFrame = ohlcvDataFrame.drop(isnaRecord.index)
        return ohlcvDataFrame
