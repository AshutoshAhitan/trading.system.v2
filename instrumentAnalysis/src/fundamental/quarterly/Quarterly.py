from pandas.core.frame import DataFrame
from ..Fundamental import Fundamental
import logging

class Quarterly(Fundamental):

    def __init__(self, configurations, dbConfigPath, symbolList) -> None:
        super().__init__(configurations, dbConfigPath, symbolList)


    def perform(self, data) -> DataFrame:

        analysedData = DataFrame(data)
        quarterly = data.quarterlyResults.iloc[0]
        print(quarterly.keys())

        self.__calculateQuarterlyTrend(quarterly)

        return analysedData

    def __calculateQuarterlyTrend(self, quarterly):
        self.__calSalesTrend(quarterly['Sales'])
        self.__calEPSTrend(quarterly['EPS in Rs'])
        self.__calNetProfitTrend(quarterly['Net Profit'])

    def __calSalesTrend(self, sales):
        logging.debug(f'Sales : {sales}')
        data = sales['data']
        data = [float(i.replace(',', '')) for i in data]

        trend = self.__calDataTrend(data)
        logging.debug(f'Sales Trend : {trend}')

        sepQuarter, decQuarter, marQuarter, junQuarter = \
        self.__calQuarterTrend(sales['Date'], data)

        return trend

    def __calEPSTrend(self, eps):
        logging.debug(f'EPS : {eps}')
        data = eps['data']
        data = [float(i) for i in data]

        trend = self.__calDataTrend(data)
        logging.debug(f'EPS Trend : {trend}')

        sepQuarter, decQuarter, marQuarter, junQuarter = \
        self.__calQuarterTrend(eps['Date'], data)

        return trend

    def __calNetProfitTrend(self, netProfit):
        logging.debug(f'Net Profit : {netProfit}')
        data = netProfit['data']
        data = [float(i.replace(',', '')) for i in data]

        trend = self.__calDataTrend(data)
        logging.debug(f'Net Profit Trend : {trend}')

        sepQuarter, decQuarter, marQuarter, junQuarter = \
        self.__calQuarterTrend(netProfit['Date'], data)

        return trend

    def __calQuarterTrend(self, dates, data):
        sepQuarterData, decQuarterData, marQuarterData, junQuarterData = \
        self.__extractQuarterData(dates, data)

        sepQuarterTrend = self.__calDataTrend(sepQuarterData)
        logging.debug(f'September Quarter Trend : {sepQuarterTrend}')

        decQuarterTrend = self.__calDataTrend(decQuarterData)
        logging.debug(f'December Quarter Trend : {decQuarterTrend}')

        marQuarterTrend = self.__calDataTrend(marQuarterData)
        logging.debug(f'March Quarter Trend : {marQuarterTrend}')

        junQuarterTrend = self.__calDataTrend(junQuarterData)
        logging.debug(f'June Quarter Trend : {junQuarterTrend}')

        return sepQuarterTrend, decQuarterTrend, marQuarterTrend, junQuarterTrend

    def __extractQuarterData(self, dates, data):
        sepQuarterData = []
        decQuarterData = []
        marQuarterData = []
        junQuarterData = []

        for idx, date in enumerate(dates):
            if 'Sep' in date:
                sepQuarterData.append(data[idx])
            elif 'Dec' in date:
                decQuarterData.append(data[idx])
            elif 'Mar' in date:
                marQuarterData.append(data[idx])
            elif 'Jun' in date:
                junQuarterData.append(data[idx])

        logging.debug(f'September Quarter Data : {sepQuarterData}')
        logging.debug(f'December Quarter Data : {decQuarterData}')
        logging.debug(f'March Quarter Data : {marQuarterData}')
        logging.debug(f'June Quarter Data : {junQuarterData}')

        return sepQuarterData, decQuarterData, marQuarterData, junQuarterData


    def __calDataTrend(self, data):
        trend = []
        for idx in range(1, len(data)):
            diff = data[idx] - data[idx-1]
            diff = diff/data[idx-1] * 100
            trend.append(diff)
        trend = [round(val, 2) for val in trend]
        logging.debug(f'Data Trend : {trend}')

        return trend
