from .exception import DataSourceException
from .yahooFinance import YahooFinance
from .Zerodha import Zerodha
from ..utils.utils import readConfigFile

class ohlcvFactory():
    @staticmethod
    def create(configPath: str, dbConfigPath: str, symbolList):
        config: dict = readConfigFile(configPath)

        if config['src'] == 'yfinance':
            return YahooFinance(config, dbConfigPath, symbolList)
        elif config['src'] == 'zerodha':
            return Zerodha(config, dbConfigPath, symbolList)
        else:
            raise DataSourceException('please provide a valid source keyword [yfinance]')
