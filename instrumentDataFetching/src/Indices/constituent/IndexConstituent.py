import logging
import pandas as pd

class IndexConstituent():

    def __init__(self, config, database) -> None:
        self.config = config
        self.database = database


    def fetch(self):

        indexContituent = pd.DataFrame([])

        for anIndex in self.config['file']:
            print(f'index : {anIndex}')
            df = pd.read_csv(self.config['file'][anIndex])
            df = df.reset_index()
            df = self._addIndexName(df, anIndex)
            df = self._renameColumns(df)
            df = self._removeUnwantedCharaters(df)
            logging.debug(f'{anIndex} index constituent : \n {df}')
            logging.debug('______________________________________')
            indexContituent = pd.concat([indexContituent, df])

        indexContituent = indexContituent.fillna(0)
        logging.debug(f'index constituent : \n {indexContituent}')
        return indexContituent

    def save(self, df):
        self.database.saveRecords(self.config['dest.table'], 
                                      self.config['dest.table.primary.keys'], 
                                      df, 
                                      self.config['dest.table.truncate'])

    def _renameColumns(self, df):

        columns = list(df.columns)
        logging.debug(f'column : {columns}')

        for columnName in self.config['column.rename']:
            if columnName in columns:
                df = df.rename(columns={columnName : self.config['column.rename'][columnName]})

        return df

    def _removeUnwantedCharaters(self, df):

        df['CompanyName'] = df['CompanyName'].str.replace("'", "")
        return df

    def _addIndexName(self, df, indexName):
        df['IndexName'] = [ indexName ] * len(df)
        return df
