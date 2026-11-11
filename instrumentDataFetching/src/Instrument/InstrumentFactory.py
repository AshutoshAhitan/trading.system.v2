from .exception import DataSourceException
from .Zerodha import Zerodha
from ..utils.utils import readConfigFile

class InstrumentFactory():
    @staticmethod
    def create(configPath: str, dbConfigPath: str):
        config: dict = readConfigFile(configPath)

        if config['src'] == 'zerodha':
            return Zerodha(config, dbConfigPath)
        else:
            raise DataSourceException('please provide a valid source keyword [zerodha]')