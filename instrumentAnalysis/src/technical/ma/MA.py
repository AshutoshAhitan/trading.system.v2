from typing import Union
from pandas.core.frame import DataFrame
from pandas.core.series import Series
from ..utils import getSubsetOfData
from ..Technical import Technical
import pandas as pd
import numpy as np
import logging

class MA(Technical):

    def __init__(self, configurations, dbConfigPath, symbolList) -> None:
        super().__init__(configurations, dbConfigPath, symbolList)
        self.maPeriod = configurations['ma.period']


    def perform(self, data) -> DataFrame:
        logging.debug(f'ohlcv data :\n {data}')

        analysedData = DataFrame(data)
        analysedData = self.__calMa(data, analysedData)
        analysedData = self.__calMaSlopeAngle(analysedData)

        analysedData = analysedData.fillna(0)
        return analysedData

    def tradingview_ema_close(self, close_values, period):
        """
        Calculate TradingView-style EMA for a sequence of close values.

        Parameters:
        - close_values: list, np.ndarray, or pd.Series of close prices
        - period: int, EMA period (default 20)

        Returns:
        - np.ndarray of EMA values (np.nan for indices < period-1)
        """
        close = np.asarray(close_values, dtype=float)
        ema = np.full_like(close, np.nan)
        if len(close) < period:
            return ema  # Not enough data for first EMA

        sma = np.mean(close[:period])
        ema[period-1] = sma
        multiplier = 2 / (period + 1)
        for i in range(period, len(close)):
            ema[i] = (close[i] - ema[i-1]) * multiplier + ema[i-1]

        ema = ema.round(2)

        return ema

    
    def __calMa(self, ohlcv: DataFrame, analysedData: DataFrame) -> DataFrame:

        for aMaPeriod, aMaType in self.maPeriod:
            if len(ohlcv) < aMaPeriod: 
                raise Exception('not enough data to calculate ma')

            colname = f'{aMaType}{aMaPeriod}'

            ma = Series([])
            if aMaType == 'sma':
                ma = ohlcv[self.configuration['ma.column']].rolling(aMaPeriod).mean().round(2)
            elif aMaType == 'ema':
                ma = self.tradingview_ema_close(ohlcv[self.configuration['ma.column']], aMaPeriod)
                # ma = ohlcv[self.configuration['ma.column']].ewm(span=aMaPeriod, adjust=False).mean().round(2)

            analysedData[colname] = ma
            logging.debug(f'> moving average of {colname} \n : {ma}')


        return analysedData


    def __calMaSlopeAngle(self, analysedData: DataFrame) -> DataFrame:

        for aMaPeriod, aMaType in self.maPeriod:
            colname = f'{aMaType}{aMaPeriod}'

            maSlope = analysedData[colname] - analysedData[colname].shift()
            maSlope = maSlope.round(2)
            logging.debug(f'> moving average slope of {colname} \n : {maSlope}')

            analysedData[f'slope{aMaType}{aMaPeriod}'] = maSlope

        return analysedData



    def searchPattern(self, maSlopeSeries: Series, pattern: str) -> bool:

        patternLength: int  = len(pattern)
        slopeValues: Union[list, Series] = maSlopeSeries.iloc[-patternLength : maSlopeSeries.size].round(2)
        slopeValues = slopeValues.to_list()


        for aSlopeValue, aSlopePattern in zip(slopeValues, pattern):
            if self.__getSign(aSlopeValue) == aSlopePattern:
                continue
            else:
                return False


        return True

    
    def __getSign(self, number: float) -> str:

        sign : str = '?'

        if number < 0: sign = '-'
        elif number >= 0: sign = '+'
        return sign
