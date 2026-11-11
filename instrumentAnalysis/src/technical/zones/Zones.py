from pandas.core.frame import DataFrame
import pandas as pd
from pandas.core.series import Series
from ..noisefilter.NoiseFilter import NoiseFilter
from ..extremas.Extremas import Extremas as MaxMin
from ..utils import getSubsetOfData
from typing import Tuple
import trendln, logging
from ..Technical import Technical

class Zones(Technical):


    def __init__(self, configurations: dict, dbConfigPath, symbolList) -> None:
        super().__init__(configurations, dbConfigPath, symbolList)

        self.maxMin = MaxMin()
        self.noiseFilter = NoiseFilter()
        self.cdlThresholdForPriceMvmntFromZone = 45
        self.minimumOhlcvCdlForZoneAnalysis = 7


    def perform(self, ohlcv: DataFrame) -> DataFrame:
        analysedData = DataFrame([])


        ohlcv = getSubsetOfData(data=ohlcv, subsetSize=len(ohlcv))
        logging.debug('> data size for analysis : {}'.format( len(ohlcv) ))


        ohlcv['minima'], ohlcv['maxima'] = self.__findMinMax(ohlcv)
        ohlcv['chg%'] = self.__calChgPercentage(ohlcv)

        logging.debug('___________________ FILTER MINIMA (START)______________________________\n')
        filteredMinimas = self.noiseFilter.filterMinima(ohlcv, ohlcv[ohlcv.minima != -1][['Datetime', 'minima']].copy(), 3)
        logging.debug('___________________ FILTER MINIMA (END)______________________________\n')

        logging.debug('_______________ ZONES ANALYSIS (START)__________________________________\n')

        for _, row in filteredMinimas.iterrows():
            logging.debug('\n')
            logging.debug(f'____________________ ZONE-{row.Datetime.strftime("%d %B, %Y")} (START) ____________________')
            logging.debug('> minima record : \n\n {}'.format(row))
            if len(DataFrame(ohlcv[ohlcv.Datetime > row.Datetime])) <= self.minimumOhlcvCdlForZoneAnalysis:
                logging.debug(f'> not enough ohlcv data for zone analysis, must be > {self.minimumOhlcvCdlForZoneAnalysis}')
                logging.debug(f'____________________ ZONE-{row.Datetime.strftime("%d %B, %Y")} (END) ____________________\n')
                continue

            zoneDetails = self.__findZoneBreadth(ohlcv, row.Datetime, row.minima)
            if len(zoneDetails) == 0:
                logging.debug(f'> zone not formed yet..')
                logging.debug(f'____________________ ZONE-{row.Datetime.strftime("%d %B, %Y")} (END) ____________________\n')
                continue

            isFalseZoneBreakout = self.__isFalseZoneBreakout(ohlcv, zoneDetails['distal']['price'], 
                                                             zoneDetails['distal']['date'], 
                                                             zoneDetails['breakoutCandle'])
            logging.debug(f'> is false zone breakout : {isFalseZoneBreakout} \n\n')
            if not isFalseZoneBreakout:
                relPriceMovement, absPriceMovementInPer, cdlCount = self.__priceMovementFromZone(ohlcv, 
                                                                     zoneDetails['distal']['price'], 
                                                                     zoneDetails['distal']['date'], 
                                                                     zoneDetails['proximal']['price'],
                                                                     zoneDetails['proximal']['date'])
                if relPriceMovement == None:
                    logging.debug(f'____________________ ZONE-{row.Datetime.strftime("%d %B, %Y")} (END) ____________________\n')
                    continue

                logging.debug(f'> number of candles occured in order to reach maximum closing price is {cdlCount}/{self.cdlThresholdForPriceMvmntFromZone }')
                analysedData = self.__addAnalysis(ohlcv, analysedData, row.Datetime, zoneDetails,
                                                  relPriceMovement, absPriceMovementInPer, cdlCount)

            logging.debug(f'____________________ ZONE-{row.Datetime.strftime("%d %B, %Y")} (END) ____________________\n')

        logging.debug('> analysed data \n {}'.format(analysedData))

        logging.debug('> filtering analysed zones based on certian criteria')
        filteredAnalysedZones: DataFrame = self.__filterAnalyzedZones(analysedData)
        logging.debug(f'\n {filteredAnalysedZones}')
        logging.debug('_______________ ZONES ANALYSIS (END)__________________________________\n')


        return filteredAnalysedZones


    def __isPriceMovedWithinSpecifiedCandlesCount(self, cdlCount):
        if cdlCount > self.cdlThresholdForPriceMvmntFromZone:
            return False
        else: return True




    def __priceMovementFromZone(self, ohlcv, distalPrice, distalPriceDate, proximalPrice, proximalPriceDate):

        immediateCandle = self.__immediateCandleClosedBelowMinima(ohlcv, distalPrice, distalPriceDate)

        if len(immediateCandle):
            candlesAboveDistalPrice = ohlcv[(ohlcv.Datetime > proximalPriceDate) & (ohlcv.Datetime < immediateCandle['Datetime'])]
        else:
            candlesAboveDistalPrice = ohlcv[ohlcv.Datetime > proximalPriceDate]

        candlesAboveDistalPrice = candlesAboveDistalPrice[:self.cdlThresholdForPriceMvmntFromZone]

        maxClosingPriceReached = candlesAboveDistalPrice.Close.max()
        cdlCount = self.__candleCount(ohlcv, proximalPriceDate, ohlcv[ohlcv.Close == maxClosingPriceReached].Datetime.to_list()[0])


        absPriceMovement = maxClosingPriceReached - proximalPrice
        absPriceMovement = round(absPriceMovement, 2)

        zoneBreadth = proximalPrice - distalPrice
        zoneBreadth = round(zoneBreadth, 2)
        logging.debug(f'> zone breadth : {zoneBreadth}/{round((zoneBreadth/distalPrice)*100, 1)}%')
        if zoneBreadth == 0:
            logging.debug('> zone breadth is 0, aborting further analysis')
            return None, None, None

        relPriceMovement = absPriceMovement/zoneBreadth
        relPriceMovement = round(relPriceMovement, 1)
        logging.debug(f'> relative price movement is {relPriceMovement}x of zone breadth within {self.cdlThresholdForPriceMvmntFromZone} candles period')

        absPriceMovementInPer = (absPriceMovement/proximalPrice) * 100
        absPriceMovementInPer = round(absPriceMovementInPer, 1)
        logging.debug(f'> absolute price movement is {absPriceMovementInPer}% of zone breadth within {self.cdlThresholdForPriceMvmntFromZone} candles period')

        return relPriceMovement, absPriceMovementInPer, cdlCount


    def __candleCount(self, ohlcv, startDate, endDate):
        return len(ohlcv[(ohlcv.Datetime > startDate) & (ohlcv.Datetime <= endDate)])




    def __isFalseZoneBreakout(self, ohlcv, distalPrice, distalPriceDate, breakoutCandle):

        immediateCandle = self.__immediateCandleClosedBelowMinima(ohlcv, distalPrice, distalPriceDate)

        if len(immediateCandle):
            candlesAfterBreakout = ohlcv[(ohlcv.Datetime > breakoutCandle['Datetime']) & (ohlcv.Datetime < immediateCandle['Datetime'])]
        else:
            candlesAfterBreakout = ohlcv[ohlcv.Datetime > breakoutCandle['Datetime']]


        maxClosePriceMovement = candlesAfterBreakout.Close.max()
        logging.debug(f'> maximum closing price movement after breakout candle : {maxClosePriceMovement}')
        logging.debug(f'> breakout candle closing price : {breakoutCandle["Close"]}')
        if maxClosePriceMovement > breakoutCandle['Close']:
            return False
        else:
            return True
        


    def __findZoneBreadth(self, ohlcv, minimaDate, minima):

        immediateCandle = self.__immediateCandleClosedBelowMinima(ohlcv, minima, minimaDate)
        logging.debug('> immediate candle closed below minima price : \n {}'.format(immediateCandle))

        if len(immediateCandle):
            chgPerMean, chgPerStd = self.__calChgPerStats(
                    ohlcv[(ohlcv.Datetime > minimaDate) & (ohlcv.Datetime < immediateCandle['Datetime'])]['chg%'],
                    removeHighVolatility=True
                    )
        else:
            chgPerMean, chgPerStd = self.__calChgPerStats(
                    ohlcv[ohlcv.Datetime > minimaDate]['chg%'],
                    removeHighVolatility=True
                    )

        chgPerThreshold = self.__calChangePerThreshold(chgPerMean, chgPerStd)
        logging.debug(f'> chg% percentage threshold : {chgPerThreshold}')

        immediateCandleAboveThreshold = self.__immediateCandleAboveChgTreshold(ohlcv, minimaDate, chgPerThreshold)
        logging.debug('> immediate candle above chg% threshold after minima : \n {}'.format(immediateCandleAboveThreshold))
        if len(immediateCandleAboveThreshold) == 0: return {}

        proximalDistalData = self.__findProximalDistalLine(ohlcv, minimaDate, minima, immediateCandleAboveThreshold)
        logging.debug(f'> proximal/distal data : {proximalDistalData}')

        return proximalDistalData




    def __calChangePerThreshold(self, chgPerMean, chgPerStd):

        chgPerThreshold = chgPerMean + chgPerStd
        chgPerThreshold = chgPerThreshold.round(1)

        return chgPerThreshold



    def __immediateCandleClosedBelowMinima(self, ohlcv, minima, minimaDate):
        immediateCandle = ohlcv[(ohlcv.Datetime > minimaDate) & (ohlcv.Close < minima)][:1]
        if len(immediateCandle):
            return immediateCandle.to_dict('records')[0]
        else: return {}



    def __immediateCandleAboveChgTreshold(self, ohlcv, minimaDate, chgPerThreshold):

        immediateCandle = ohlcv[(ohlcv.Datetime > minimaDate) & (ohlcv['chg%'] > chgPerThreshold)][:1]
        if len(immediateCandle):
            return immediateCandle.to_dict('records')[0]
        else: return {}



    def __calChgPercentage(self, ohlcv):

        ltpchgPercentage = ((ohlcv.Close - ohlcv.Close.shift())/ohlcv.Close)*100
        ltpchgPercentage = ltpchgPercentage.round(1)

        return ltpchgPercentage



    def __calChgPerStats(self, chgPercentageData, removeHighVolatility):

        chgPercentageMean = chgPercentageData.abs().mean().round(1)
        chgPercentageStd = chgPercentageData.abs().std().round(1)
        logging.debug(f'> chg% mean : {chgPercentageMean} chg% std : {chgPercentageStd}')

        volatilityThreshold = chgPercentageMean + (2 * chgPercentageStd) 

        if removeHighVolatility == True:
            df: DataFrame = DataFrame(chgPercentageData)
            volatilityRemovedData = DataFrame(df[df['chg%'].abs() <= volatilityThreshold])
            mean = volatilityRemovedData['chg%'].abs().mean().round(1); std = volatilityRemovedData['chg%'].abs().std().round(1)
            logging.debug(f'> (volatility removed) chg% mean : {mean} chg% std : {std}')
            return mean, std
        else:
            return chgPercentageMean, chgPercentageStd




    def __findProximalDistalLine(self, ohlcv, minimaDate, minima, immediateCandleAboveThreshold):

        candlesAtZone = ohlcv[(ohlcv.Datetime >= minimaDate) & (ohlcv.Datetime < immediateCandleAboveThreshold['Datetime'])]
        logging.debug(f'> candles at zones \n {candlesAtZone}')

        distalPrice = minima; distalPriceDate = minimaDate
        logging.debug(f'> distal price and date : {distalPrice} {distalPriceDate}')


        if candlesAtZone.Close.max() > candlesAtZone.Open.max():
            proximalPrice = candlesAtZone.Close.max()
            proximalPriceDate = candlesAtZone[candlesAtZone.Close == proximalPrice].Datetime
        else:
            proximalPrice = candlesAtZone.Open.max()
            proximalPriceDate = candlesAtZone[candlesAtZone.Open == proximalPrice].Datetime
        
        proximalPriceDate = proximalPriceDate.to_list()[0]
        logging.debug(f'> proximal price and date : {proximalPrice} {proximalPriceDate}')

        zoneBreadth = ((proximalPrice-distalPrice)/distalPrice) * 100
        zoneBreadth = round(zoneBreadth, 1)


        return {
                'distal' : { 'price' : distalPrice, 'date' : distalPriceDate },
                'proximal' : { 'price' : proximalPrice, 'date' : proximalPriceDate },
                'candlesAtZone' : candlesAtZone,
                'numberOfCandlesAtZone' : len(candlesAtZone),
                'breakoutCandle' : immediateCandleAboveThreshold,
                'zoneBreadth' : zoneBreadth
        }




    def __findMinMax(self, ohlcv: DataFrame, method: int=trendln.METHOD_NUMDIFF) -> Tuple[Series, Series]:

        maxima = self.maxMin.getMaximaPoints(ohlcv['High'], method)
        minima = self.maxMin.getMinimaPoints(ohlcv['Low'], method)

        return minima, maxima



    def __addAnalysis(self, ohlcv, analysedData, date,  zoneDetails, relPriceMovement, absPriceMovementInPer, cdlCount):

        symbol = ohlcv.Symbol.to_list()[0]
        timeframe = ohlcv.Timeframe.to_list()[0]

        analysedData = pd.concat([analysedData, DataFrame({
            'Symbol' : symbol,
            'Timeframe' : timeframe,
            'Datetime' : [date],
            'distalPriceDate' : [zoneDetails['distal']['date'].date()],
            'distalPrice' : [zoneDetails['distal']['price']],
            'proximalPriceDate' : [zoneDetails['proximal']['date'].date()],
            'proximalPrice' : [zoneDetails['proximal']['price']],
            'zoneBreadth' : [zoneDetails['zoneBreadth']],
            'relPriceMovement' : [relPriceMovement],
            'absPriceMovementInPer' : [absPriceMovementInPer],
            'numberOfCandlesAtZone' : [zoneDetails['numberOfCandlesAtZone']],
            'cdlCount' : cdlCount,
            'breakoutCandleDate' : [zoneDetails['breakoutCandle']['Datetime']]
        })])

        return analysedData

    def __filterAnalyzedZones(self, analysedData) -> DataFrame:

        filteredAnalysedZones = DataFrame([])

        meanRelativePriceMovement = analysedData.relPriceMovement.mean()
        meanRelativePriceMovement = int(meanRelativePriceMovement)
        logging.debug(f'> relative price movement threshold {meanRelativePriceMovement}')

        meanAbsPriceMovementInPer = analysedData.absPriceMovementInPer.mean()
        meanAbsPriceMovementInPer = int(meanAbsPriceMovementInPer)
        logging.debug(f'> absolute price movement threshold {meanAbsPriceMovementInPer}')

        filteredAnalysedZones = DataFrame(analysedData[(analysedData.relPriceMovement >= meanRelativePriceMovement) &
                                             (analysedData.absPriceMovementInPer >= meanAbsPriceMovementInPer)])

        filteredAnalysedZones = DataFrame(filteredAnalysedZones[filteredAnalysedZones.relPriceMovement >= 2])

        return filteredAnalysedZones
