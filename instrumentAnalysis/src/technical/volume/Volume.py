from pandas.core.frame import DataFrame
from pandas.core.series import Series
from ..Technical import Technical
import logging

class Volume(Technical):

    def __init__(self, configurations, dbConfigPath, symbolList) -> None:
        super().__init__(configurations, dbConfigPath, symbolList)
        self.maPeriod = configurations['ma.period']


    def perform(self, data) -> DataFrame:
        logging.debug(f'> ohlcv data \n {data}')

        analysedData = DataFrame(data)
        analysedData = self.__calMa(data, analysedData)

        analysedData = analysedData.fillna(0)

        return analysedData


    def __calMa(self, ohlcv: DataFrame, analysedData: DataFrame) -> DataFrame:

        for aMaPeriod in self.maPeriod:
            if len(ohlcv) < aMaPeriod: raise Exception('not enough data to calculate ma')

            colname = 'ma{}'.format(aMaPeriod)

            ma = Series([])
            ma = ohlcv[self.configuration['ma.column']].rolling(aMaPeriod).mean().round(2)

            analysedData[colname] = ma
            logging.debug(f'> moving average of {colname} \n : {ma}')


        return analysedData


