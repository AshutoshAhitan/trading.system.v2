import logging
from pandas import DataFrame
import pandas as pd


class NoiseFilter():

    def __init__(self) -> None:
        pass

    def filterMinima(self, ohlcv, minimaList, upSwingFromMinima):
        filteredMinima = DataFrame()
        leftoutMinima = DataFrame()

        # minimaList = minimaList[minimaList.Date == '2022-08-23']
        logging.debug('> minima list : \n {}'.format(minimaList))

        for _, row in minimaList.iterrows():
            minimaDatetime, minima = row.Datetime, row.minima

            immediateCandle = self.__immediateCandleClosedBelowMinima(ohlcv, minima, minimaDatetime)
            logging.debug('> immediate candle closed below minima price : \n {}'.format(immediateCandle))
            if len(immediateCandle) == 0:
                filteredMinima = pd.concat([filteredMinima, DataFrame({'Datetime' : [row.Datetime], 'minima' : [row.minima]})])
            else:

                peakClosingPrice = self.__getPeakClosingPrice(ohlcv, startDate=minimaDatetime, endDate=immediateCandle['Datetime'])
                logging.debug('> peak closing price : {}'.format(peakClosingPrice))

                minimaCandleRange = self.__calCandleRange(ohlcv, minimaDatetime)
                logging.debug(f'> minima candle range : {minimaCandleRange}')
                if minimaCandleRange == 0:
                    logging.debug('> minima candle range is 0 [aborting analysis]')
                    continue

                isPeakClosingPriceAboveThreshold = self.__isPeakClosingPriceAboveThreshold(minima, peakClosingPrice,
                                                                                   minimaCandleRange, upSwingFromMinima)
                logging.debug(f'> is peak closing price above threshold : {isPeakClosingPriceAboveThreshold}')
                if isPeakClosingPriceAboveThreshold == True:
                    filteredMinima = pd.concat([filteredMinima, DataFrame({'Datetime' : [row.Datetime], 'minima' : [row.minima]})])
                else:
                    leftoutMinima = pd.concat([leftoutMinima, DataFrame({'Datetime' : [row.Datetime], 'minima' : [row.minima]})])



        logging.debug('> filtered minimas {}/{} : \n {}'.format(len(filteredMinima), len(minimaList), filteredMinima))
        logging.debug('> leftout minimas {}/{} : \n {}'.format(len(leftoutMinima), len(minimaList), leftoutMinima))

        return filteredMinima



    def filterMaxima(self, ohlcv, maximaList, downSwingFromMaxima):
        pass


    def __calCandleRange(self, ohlcv, date):
        candle = ohlcv[ohlcv.Datetime == date].to_dict('records')[0]
        range = candle['High'] - candle['Low']
        return round(range, 0)


    def __immediateCandleClosedBelowMinima(self, ohlcv, minimaPrice, minimaDate):
        immediateCandle = ohlcv[(ohlcv.Datetime > minimaDate) & (ohlcv.Close < minimaPrice)][:1]
        if len(immediateCandle):
            return immediateCandle.to_dict('records')[0]
        else: return {}


    def __getPeakClosingPrice(self, ohlcv, startDate, endDate):
        return ohlcv[(ohlcv.Datetime > startDate) & (ohlcv.Datetime < endDate)].Close.max()


    def __isPeakClosingPriceAboveThreshold(self, minimaPrice, peakClosingPrice, candleRange, threshold):
        if ((peakClosingPrice - minimaPrice)/candleRange > threshold):
            return True
        else:
            return False
