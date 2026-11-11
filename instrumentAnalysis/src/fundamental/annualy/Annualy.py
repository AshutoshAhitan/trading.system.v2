from pandas.core.frame import DataFrame
from ..Fundamental import Fundamental
import logging

class Annualy(Fundamental):

    def __init__(self, configurations, dbConfigPath, symbolList) -> None:
        super().__init__(configurations, dbConfigPath, symbolList)


    def perform(self, data) -> DataFrame:

        analysedData = DataFrame(data)
        annualResults = data.annualResults.iloc[0]
        print(annualResults.keys())

        self.__calculateAnnualTrend(annualResults)

        return analysedData

    def __calculateAnnualTrend(self, annualResults):
        self.__calSalesTrend(annualResults['Sales'])
        self.__calEPSTrend(annualResults['EPS in Rs'])
        self.__calNetProfitTrend(annualResults['Net Profit'])

    def __calSalesTrend(self, sales):
        logging.debug(f'Sales : {sales}')
        data = sales['data']
        data = [float(i.replace(',', '')) for i in data]

        trend = self.__calDataTrend(data)
        logging.debug(f'Sales Trend : {trend}')

        return trend

    def __calEPSTrend(self, eps):
        logging.debug(f'EPS : {eps}')
        data = eps['data']
        data = [float(i) for i in data]

        trend = self.__calDataTrend(data)
        logging.debug(f'EPS Trend : {trend}')

        return trend

    def __calNetProfitTrend(self, netProfit):
        logging.debug(f'Net Profit : {netProfit}')
        data = netProfit['data']
        data = [float(i.replace(',', '')) for i in data]

        trend = self.__calDataTrend(data)
        logging.debug(f'Net Profit Trend : {trend}')

        return trend

    def __calDataTrend(self, data):
        trend = []
        for idx in range(1, len(data)):
            diff = data[idx] - data[idx-1]
            diff = diff/data[idx-1] * 100
            trend.append(diff)
        trend = [round(val, 2) for val in trend]
        logging.debug(f'Data Trend : {trend}')

        return trend
