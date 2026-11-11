from abc import ABC, abstractmethod

from pandas import DataFrame


class Sectors(ABC):

    def __init__(self, config, database) -> None:
        super().__init__()
        self.configuration = config
        self.database = database

    @abstractmethod
    def fetch(self):
        pass


    def save(self, records):
        self.database.saveRecords(self.configuration['dest.table'], self.configuration['dest.table.primary.keys'],
                                  records, self.configuration['dest.table.truncate'])
