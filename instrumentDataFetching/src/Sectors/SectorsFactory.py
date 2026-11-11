
from .MoneyControlSectors import MoneyControlSectors
from .FinologySectors import FinologySectors
from .BSESectors import BSESectors
from .NSESectors import NSESectors
from ..utils.utils import readConfigFile
from ..Database.DatabaseFactory import DatabaseFactory

class SectorsFactory:

    @staticmethod
    def create(configPath: str, dbConfigPath: str):

        config: dict = readConfigFile(configPath)
        database = DatabaseFactory.create(dbConfigPath)

        sectors = None; src = config['src']
        if src == 'finology':
            sectors = FinologySectors(config[src], database)
        elif src == 'moneycontrol':
            sectors = MoneyControlSectors(config)
        elif src == 'bse':
            sectors = BSESectors(config[src], database)
        elif src == 'nse':
            sectors = NSESectors(config[src], database)
        else:
            raise Exception("src is invalid. provide valid src [finology/moneycontrol/bse/nse]")

        return sectors

