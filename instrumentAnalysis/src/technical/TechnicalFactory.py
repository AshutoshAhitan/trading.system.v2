from .TechnicalExceptions import InvalidTechnicalAnalysisName
from .volatility.Volatility import Volatility
from .ma.MA import MA
from .volume.Volume import Volume
from .zones.Zones import Zones
from .candlestick.CandleStick import CandleStick
from .pricerange.PriceRange import PriceRange
from .slope.Slope import Slope
from .adx.ADX import ADX
from .candlestick.HACandleStick import HACandleStick
from .ma.HeikinAshiMA import HeikinAshiMA
from .openInterest.OpenInterest import OpenInterest
from typing import Optional
import json


class TechnicalFactory:

    @staticmethod
    def create(configPath: str, dbConfigPath: str, symbolList, **kargs):

        technicalAnalysisName = kargs['technicalAnalysisName']
        configurations = TechnicalFactory.readConfigFile(configPath)

        if technicalAnalysisName == 'ma': 
            return MA(configurations, dbConfigPath, symbolList)
        elif technicalAnalysisName == 'volatility':
            return Volatility(configurations, dbConfigPath, symbolList)
        elif technicalAnalysisName == 'zones':
            return Zones(configurations, dbConfigPath, symbolList)
        elif technicalAnalysisName == 'candlestick':
            return CandleStick(configurations, dbConfigPath, symbolList)
        elif technicalAnalysisName == 'pricerange':
            return PriceRange(configurations, dbConfigPath, symbolList)
        elif technicalAnalysisName == 'slope':
            return Slope(configurations, dbConfigPath, symbolList)
        elif technicalAnalysisName == 'adx':
            return ADX(configurations, dbConfigPath, symbolList)
        elif technicalAnalysisName == 'heikinAshiCandlestick':
            return HACandleStick(configurations, dbConfigPath, symbolList)
        elif technicalAnalysisName == 'heikinAshiMA':
            return HeikinAshiMA(configurations, dbConfigPath, symbolList)
        elif technicalAnalysisName == 'oi':
            return OpenInterest(configurations, dbConfigPath, symbolList)
        
        else: raise InvalidTechnicalAnalysisName


    @staticmethod
    def readConfigFile(configPath: str):

        configurations: Optional[dict] = None
        with open(configPath) as file:
            content = file.read()
            configurations = json.loads(content)
            assert configurations != None

        return configurations
