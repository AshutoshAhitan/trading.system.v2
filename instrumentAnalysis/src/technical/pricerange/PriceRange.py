from ..Technical import Technical
from pandas.core.frame import DataFrame
import logging


class PriceRange(Technical):

    def __init__(self, configurations, dbConfigPath, symbolList) -> None:
        super().__init__(configurations, dbConfigPath, symbolList)

    def perform(self, data) -> DataFrame:
        logging.debug(' data : {}'.format(data))

        analysedData = DataFrame(data)
        analysedData = self.__calPriceRange(analysedData)

        return analysedData

    def __calPriceRange(self, analysedData : DataFrame) -> DataFrame:
        # list containing days for which price range is to be calculated
        # values are coming from configurations
        priceRangeDays = self.configuration['price.range.days']

        # iterate over each day in priceRangeDays
        for priceRangeDay in priceRangeDays:
            # add column to analysedData for price range
            analysedData['priceRange{}'.format(priceRangeDay)] = [0] * len(analysedData)

            # length of analysedData
            length = len(analysedData)

            # calculate price range for priceRangeDay
            # price range is difference between max and min of price of Close of analysedData
            for i in range(0, len(analysedData), priceRangeDay):
                idx = length - i
                priceCloseMax = analysedData.Close.iloc[idx-priceRangeDay: idx].max()
                priceOpenMax = analysedData.Open.iloc[idx-priceRangeDay: idx].max()
                priceMax = max(priceCloseMax, priceOpenMax)

                priceCloseMin = analysedData.Close.iloc[idx-priceRangeDay: idx].min()
                priceOpenMin = analysedData.Open.iloc[idx-priceRangeDay: idx].min()
                priceMin = min(priceCloseMin, priceOpenMin)

                PriceRange = ((priceMax - priceMin) / priceMin) * 100

                # store the calculated price range in analysedData
                analysedData['priceRange{}'.format(priceRangeDay)].iloc[idx-priceRangeDay: idx] = PriceRange

                # round to 1 decimal places
                analysedData['priceRange{}'.format(priceRangeDay)] = analysedData['priceRange{}'.format(priceRangeDay)].round(1)

                # calculate moving average of price range and store in analysedData
                analysedData['priceRange{}ma'.format(priceRangeDay)] = \
                analysedData['priceRange{}'.format(priceRangeDay)].rolling(priceRangeDay).mean().round(1)

                # remove nan values from the calculated moving average
                analysedData['priceRange{}ma'.format(priceRangeDay)] = analysedData['priceRange{}ma'.format(priceRangeDay)].fillna(0)

            logging.debug(f'> price range of {priceRangeDay} \n : {analysedData["priceRange{}".format(priceRangeDay)].tail(21)}')

        return analysedData
        
