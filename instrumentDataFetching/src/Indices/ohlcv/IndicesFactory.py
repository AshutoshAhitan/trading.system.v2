from .Zerodha import Zerodha
from ...utils.utils import readConfigFile

class IndicesFactory():

    @staticmethod
    def create(configPath: str, dbConfigPath: str, symbolList):
        config: dict = readConfigFile(configPath)
        return Zerodha(config, dbConfigPath, symbolList)
