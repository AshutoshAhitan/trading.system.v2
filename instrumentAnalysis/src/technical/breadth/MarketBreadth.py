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
