from .quarterly.Quarterly import Quarterly
from .annualy.Annualy import Annualy
from .FundamentalExceptions import InvalidTechnicalAnalysisName
from typing import Optional
import json


class FundamentalFactory:

    @staticmethod
    def create(configPath: str, dbConfigPath: str, symbolList, **kargs):

        analysisName = kargs['analysisName']
        configurations = FundamentalFactory.readConfigFile(configPath)

        if analysisName == 'quarterly':
            return Quarterly(configurations, dbConfigPath, symbolList)
        elif analysisName == 'annualy':
            return Annualy(configurations, dbConfigPath, symbolList)
        else: raise InvalidTechnicalAnalysisName


    @staticmethod
    def readConfigFile(configPath: str):

        configurations: Optional[dict] = None
        with open(configPath) as file:
            content = file.read()
            configurations = json.loads(content)
            assert configurations != None

        return configurations
