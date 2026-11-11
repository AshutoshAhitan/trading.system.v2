from .Zerodha import Zerodha
from ...utils.utils import readConfigFile

class StrikePriceFactory():

    @staticmethod
    def create(configPath: str, dbConfigPath: str):
        config: dict = readConfigFile(configPath)
        return Zerodha(config, dbConfigPath)
