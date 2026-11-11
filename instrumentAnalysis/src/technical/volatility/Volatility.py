from pandas.core.frame import DataFrame
from ..Technical import Technical
import logging

class Volatility(Technical):

    def __init__(self, configurations, dbConfigPath, symbolList) -> None:
        super().__init__(configurations, dbConfigPath, symbolList)


    def perform(self, data) -> DataFrame:
        logging.debug(f'> ohlcv data \n {data}')

        analysedData = DataFrame(data)
        analysedData = self.__calClosePctChange(data, analysedData)
        analysedData = self.__calOpenPctChange(data, analysedData)
        analysedData = self.__calRangePctChange(data, analysedData)
        analysedData = self.__calBodyPctChange(data, analysedData)
        analysedData = analysedData.fillna(0)

        return analysedData

    def __calClosePctChange(self, ohlcv, analysedData):

        pctChange = ohlcv.Close.pct_change()
        pctChange = pctChange * 100
        pctChange = pctChange.round(2)
        logging.debug(f'> candle close pct change is : \n {pctChange}')

        analysedData['candleClosePctChange'] = pctChange

        return analysedData


    def __calOpenPctChange(self, ohlcv, analysedData):

        pctChange = ohlcv.Open.pct_change()
        pctChange = pctChange * 100
        pctChange = pctChange.round(2)
        logging.debug(f'> candle open pct change is : \n {pctChange}')

        analysedData['candleOpenPctChange'] = pctChange

        return analysedData


    def __calRangePctChange(self, ohlcv, analysedData):

        rangeMedian = (ohlcv.High + ohlcv.Low)/2
        logging.debug(f'> candle range meadian : \n {rangeMedian}')

        pctChange = rangeMedian.pct_change()
        pctChange = pctChange * 100
        pctChange = pctChange.round(2)
        logging.debug(f'> candle range pct change is : \n {pctChange}')

        analysedData['candleRangePctChange'] = pctChange

        return analysedData


    def __calBodyPctChange(self, ohlcv, analysedData):

        bodyMedian = (ohlcv.Open + ohlcv.Close)/2
        logging.debug(f'> candle body meadian : \n {bodyMedian}')

        pctChange = bodyMedian.abs().pct_change()
        pctChange = pctChange * 100
        pctChange = pctChange.round(2)
        logging.debug(f'> candle body change is : \n {pctChange}')

        analysedData['candleBodyPctChange'] = pctChange

        return analysedData
