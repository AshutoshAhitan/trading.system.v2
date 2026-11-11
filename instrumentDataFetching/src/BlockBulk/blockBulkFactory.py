from ..utils.utils import readConfigFile
from .blockBulk import BlockBulk

class BlockBulkFactory:

    @staticmethod
    def create(configPath: str):
        config: dict = readConfigFile(configPath)
        return BlockBulk(config)
