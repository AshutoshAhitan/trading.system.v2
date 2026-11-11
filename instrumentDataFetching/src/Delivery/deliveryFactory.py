from .exception import DataSourceException
from .nse import NSE
from .nsepy import NSEpy
from ..utils.utils import readConfigFile

class DeliveryFactory:
    @staticmethod
    def create(configPath: str, dbConfigPath: str, symbolList):
        config: dict = readConfigFile(configPath)
        if config['src'] == 'nsepy':
            # TODO
            return NSEpy(config)
        elif config['src'] == 'nse':
            return NSE(config, dbConfigPath, symbolList)
        else:
            raise DataSourceException('Data source not provided. valid keywords are [nse]')
