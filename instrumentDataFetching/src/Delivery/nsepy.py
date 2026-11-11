from pandas.core.arrays import period
from .delivery import Delivery
from typing import Optional
from .exception import DateNotProviedException
from nsepy import get_history
from datetime import datetime
from ..utils.utils import getStartDateEndDate
from pandas import DataFrame

class NSEpy(Delivery):

    def __init__(self, config: dict) -> None:
        self.period = config['period']
        self.startDate = 'startDate' in config or None
        self.endDate = 'endDate' in config or None

        pass


    def fetchData(self, symbol: str) -> DataFrame:

        period= self.period; startDate = self.startDate; endDate = self.endDate

        if (period == None) and (startDate == None and endDate == None):
            raise DateNotProviedException('Please provide starting date and ending date or preiod')
        elif (startDate != None) and (endDate == None):
            raise DateNotProviedException('Please provide end date')
        elif (startDate == None) and (endDate != None):
            raise DateNotProviedException('Please provide start date')

        if period != None:
            startDate, endDate  = getStartDateEndDate(period)
            data: DataFrame     = get_history(symbol, start=startDate, end=endDate)
        else:
            startDate   = datetime.fromisoformat(startDate)
            endDate     = datetime.fromisoformat(endDate)
            data        = get_history(symbol, start=startDate, end=endDate)

        data = data.fillna(0)
        # data = self._calInvestedAmount(ohlcvDataFrame=data)
        # data.fillna(0)

        return data


    def _calInvestedAmount(self, ohlcvDataFrame: DataFrame) -> DataFrame:

        ohlcvDataFrame['investedAmount'] = ohlcvDataFrame['Close'] * ohlcvDataFrame['Deliverable Volume']
        return ohlcvDataFrame
