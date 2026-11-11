from ...utils.utils import readConfigFile
from .IndexConstituent import IndexConstituent
from ...Database.DatabaseFactory import DatabaseFactory

class IndexConstituentFactory(object):

    @staticmethod
    def create(configPath: str, dbConfigPath: str):

        config: dict = readConfigFile(configPath)
        database = DatabaseFactory.create(dbConfigPath)

        return IndexConstituent(config['index.constituent'], database)

