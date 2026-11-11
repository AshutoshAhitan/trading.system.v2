import logging
from .Sectors import Sectors
import pandas as pd

class NSESectors(Sectors):

    def __init__(self, config, database) -> None:
        super().__init__(config, database)
        self.config = config


    def fetch(self):
        df = pd.read_csv(self.config['equities.file.path'] + '/' + self.config['equities.file.name'])
        df = df.reset_index()
        df =self._renameColumns(df)

        df['company'] = df['company'].str.replace("'",'')
        logging.debug(f' industries : \n {df}')
        return df

    def _renameColumns(self, ohlcvDataFrame):

        columns = list(ohlcvDataFrame.columns)

        for columnName in self.config['columns.rename']:
            if columnName in columns:
                ohlcvDataFrame = ohlcvDataFrame.rename(columns={columnName : self.config['columns.rename'][columnName]})

        return ohlcvDataFrame

        


