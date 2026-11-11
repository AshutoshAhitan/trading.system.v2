import logging
from .Sectors import Sectors
import pandas as pd

class BSESectors(Sectors):

    def __init__(self, config, database) -> None:
        super().__init__(config, database)
        self.config = config


    def fetch(self):
        df = pd.read_csv(self.config['equities.file.path'] + '/' + self.config['equities.file.name'])
        df = df.reset_index()
        df = pd.DataFrame(df[df.Status == 'Active'])
        df = df.rename(columns={
            "Security Id" : self.config['columns.rename']['Security Id'],
            "Security Name" : self.config['columns.rename']['Security Name'],
            "Industry New Name": self.config['columns.rename']['Industry New Name'], 
            "Igroup Name": self.config['columns.rename']['Igroup Name'],
            "ISubgroup Name" : self.config['columns.rename']['ISubgroup Name']})

        df['securityName'] = df['securityName'].str.replace("'",'')
        logging.debug(f' industries : \n {df}')
        return df

        


