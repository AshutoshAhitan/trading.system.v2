from pandas.core.frame import DataFrame
from ..Technical import Technical
import numpy as np
import logging

class CandleStick(Technical):

    def __init__(self, configurations, dbConfigPath, symbolList) -> None:
        super().__init__(configurations, dbConfigPath, symbolList)
        self.configurations = configurations
        self.candleOpenCol = self.configurations.get('candle.open', 'Open')
        self.candleHighCol = self.configurations.get('candle.high', 'High')
        self.candleLowCol = self.configurations.get('candle.low', 'Low')
        self.candleCloseCol = self.configurations.get('candle.close', 'Close')


    def perform(self, data) -> DataFrame:

        analysedData = DataFrame(data)
        analysedData = self.__calRange(data, analysedData)
        analysedData = self.__calBodyRange(data, analysedData)
        analysedData = self.__calBullishness(data, analysedData)
        analysedData = self.__calLowerWickRelSize(data, analysedData)
        analysedData = analysedData.fillna(0)

        return analysedData

    # create function to calculate candlestick body range
    def __calBodyRange(self, ohlcv: DataFrame, analysedData: DataFrame) -> DataFrame:

        analysedData['candleBodyRange'] = ohlcv[self.candleCloseCol] - ohlcv[self.candleOpenCol]

        # calculate absolute value of the candlestick body range
        analysedData['candleBodyRange'] = analysedData.candleBodyRange.abs()

        analysedData['candleBodyRange'] = analysedData.candleBodyRange.round(1)

        return analysedData

    def __calRange(self, ohlcv: DataFrame, analysedData: DataFrame) -> DataFrame:

        analysedData['candleRange'] = ohlcv[self.candleHighCol] - ohlcv[self.candleLowCol]
        analysedData['candleRange'] = analysedData.candleRange.round(1)

        return analysedData

    def __calBullishness(self, ohlcv: DataFrame, analysedData: DataFrame) -> DataFrame:

        analysedData['candleBullishness'] = (ohlcv[self.candleCloseCol]-ohlcv[self.candleOpenCol])/(ohlcv[self.candleHighCol]-ohlcv[self.candleLowCol])
        analysedData['candleBullishness'] = analysedData.candleBullishness.round(1)*100
        analysedData.replace([np.inf, -np.inf], np.nan, inplace=True)

        return analysedData

    def __calLowerWickRelSize(self, ohlcv: DataFrame, analysedData: DataFrame) -> DataFrame:

        analysedData['isBullish'] = [False]*len(ohlcv)
        analysedData.loc[(analysedData[self.candleCloseCol]-analysedData[self.candleOpenCol]) >= 0, 'isBullish'] = True
        logging.debug(' candle bullish/bearish:\n {analysedData}')


        # analysedData['candleLowerWickRelSize'] =[0]*len(analysedData)
        analysedData['candleLowerWickRelSize'] = 0.0

        ohlcvHigh = ohlcv[self.candleHighCol]
        ohlcvLow = ohlcv[self.candleLowCol]
        ohlcvOpen = ohlcv[self.candleOpenCol]
        ohlcvClose = ohlcv[self.candleCloseCol]

        analysedData.loc[analysedData.isBullish == True, 'candleLowerWickRelSize'] = \
            ((ohlcvHigh-ohlcvLow)-(ohlcvHigh-ohlcvOpen))/(ohlcvHigh-ohlcvLow)

        analysedData.loc[analysedData.isBullish == False, 'candleLowerWickRelSize'] = \
            ((ohlcvHigh-ohlcvLow)-(ohlcv.High-ohlcvClose))/(ohlcvHigh-ohlcvLow)

        analysedData['candleLowerWickRelSize'] = analysedData.candleLowerWickRelSize.round(1)*100

        analysedData = analysedData.drop('isBullish', axis=1)
        analysedData.replace([np.inf, -np.inf], np.nan, inplace=True)

        return analysedData
