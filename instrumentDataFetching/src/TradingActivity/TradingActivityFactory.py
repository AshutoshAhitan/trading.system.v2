from .TradingAcitvity import TradingActivity
from ..utils.utils import readConfigFile
from ..Database.DatabaseFactory import DatabaseFactory

class TradingActivityFactory():

    @staticmethod
    def create(configPath, dbConfigPath):

        config = readConfigFile(configPath)
        database = DatabaseFactory.create(dbConfigPath)

        tradingActivity = TradingActivity(config, database)
        return tradingActivity

