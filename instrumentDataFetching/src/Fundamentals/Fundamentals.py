from .yahooFinance.YahooFinance import YahooFinance
from .screener.Screener import Screener
from .nse.NSE import NSE
from ..utils.utils import readConfigFile

class Fundamentals(object):

    def __init__(self, configPath, dbConfigPath, symbolList) -> None:
        config: dict = readConfigFile(configPath)
        self.nse = NSE(config, dbConfigPath, symbolList)
        self.screener = Screener(config, dbConfigPath, symbolList)
        self.config = config


    def fetch(self):
        if self.config['fundamentals']['nse.fetch'] == True:
            self.nse.fetch()

        if self.config['fundamentals']['screener.fetch'] == True:
            self.screener.fetch()
