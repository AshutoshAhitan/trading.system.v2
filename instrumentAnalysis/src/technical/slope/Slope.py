from pandas.core.frame import DataFrame
from ..Technical import Technical
import logging

class Slope(Technical):

    def __init__(self, configurations, dbConfigPath, symbolList) -> None:
        super().__init__(configurations, dbConfigPath, symbolList)

    def perform(self, data) -> DataFrame:
        logging.debug(f'> ohlcv data \n {data}')

        analysedData = DataFrame(data)
        analysedData = self.__calculateSlope(analysedData)

        return analysedData

    def __calculateSlope(self, analysedData) -> DataFrame:
        length = len(analysedData)
        logging.debug(f'> length : {length}')

        offset = 3

        analysedData['slope3'] = [0] * len(analysedData)

        for i in range(0, len(analysedData), offset):
            idx = length - i - 1

            priceCloseLatest = analysedData.Close.iloc[idx]
            priceClosePrevious = analysedData.Close.iloc[idx-offset]

            slope = ((priceCloseLatest - priceClosePrevious) / priceClosePrevious) * 100

            # round to 0 decimal places
            slope = round(slope, 0)

            analysedData['slope3'].iloc[idx-offset: idx] = slope

        logging.debug(f'> slope3 \n : {analysedData["slope3"].tail(21)}')

        return analysedData

