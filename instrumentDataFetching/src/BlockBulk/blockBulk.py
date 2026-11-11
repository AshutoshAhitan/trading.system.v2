from typing import Dict
from dateutil import parser
from pandas import DataFrame
import pandas
from bs4 import BeautifulSoup
from bs4.element import ResultSet
from ..utils.communication import Communication
from typing import List
from io import StringIO
from dateutil.parser import parse
import re

class BlockBulk:

    def __init__(self, config: dict) -> None:

        self.communication = Communication(config['url'])
        self.headers    = config['headers']
        self.payload    = config['payload']
        self.method     = config['method']
        self.blockPath  = config['path']['block']
        self.bulkPath   = config['path']['bulk']


    def fetch(self) -> DataFrame:

        data = DataFrame([])

        block   = self.__fetchBlockDeals()
        bulk    = self.__fetchBulkDeals()

        data = pandas.concat([block, bulk])
        data = self.__renameColumns(data)
        data = self.__normalise(data)
        data = self.__netTradedQuantityNotZero(data)

        return data


    def __netTradedQuantityNotZero(self, data) -> DataFrame:
        
        quantityTradedDf = pandas.DataFrame([])
        quantityTradedDf['Date'] = data.Date
        quantityTradedDf['Symbol'] = data.Symbol
        quantityTradedDf['netQuantityTraded'] = data.QuantityTraded

        grpbyResult = quantityTradedDf.groupby(['Date', 'Symbol'])
        res = grpbyResult.sum()
        res = res[res.netQuantityTraded != 0]
        res = res.reset_index()

        data = pandas.merge(data, res, on=['Date', 'Symbol'])

        return data



    def __renameColumns(self, data: DataFrame) -> DataFrame:

        data = data.rename(columns={
            "Security Name" : "SecurityName",
            "Client Name"   : "ClientName",
            "Buy / Sell"    : "BuySell",
            "Quantity Traded " : "QuantityTraded",
            "Trade Price / Wght. Avg. Price" : "TradePriceWghtAvgPrice",
        })

        return data


    def __normalise(self, data: DataFrame) -> DataFrame:

        data['Date'] = list(map(self.__normaliseDate, data['Date']))
        data['QuantityTraded'] = list(map(self.__normaliseRows, data['QuantityTraded']))
        data['ClientName'] = list(map(self.__normaliseRows, data['ClientName']))

        data.QuantityTraded = data['QuantityTraded'].astype(str).astype(int)
        data.loc[data.BuySell == 'SELL', ['QuantityTraded']] *= -1

        return data



    def __fetchBlockDeals(self) -> DataFrame:

        htmlData = self.communication.fetch(self.method, self.blockPath, self.payload, self.headers)
        soup        = BeautifulSoup(htmlData, 'html.parser')
        csvString   = soup.findAll('div', id='csvContentDiv')[0].text
        data = self.__parseCsvToDataFrame(csvString)
        data['Type'] = ['BLOCK']*len(data)

        return data


    def __fetchBulkDeals(self) -> DataFrame:

        htmlData = self.communication.fetch(self.method, self.bulkPath, self.payload, self.headers)
        soup        = BeautifulSoup(htmlData, 'html.parser')
        csvString   = soup.findAll('div', id='csvContentDiv')[0].text
        data = self.__parseCsvToDataFrame(csvString)

        data['Type'] = ['BULK']*len(data)

        return data


    def __parseCsvToDataFrame(self, csvString: str) -> DataFrame:

        csvString = re.sub(r':', '\n', csvString)
        csvString = StringIO(csvString)
        df: DataFrame = pandas.read_csv(csvString)

        return df


    def __normaliseRows(self, text: str) -> str:

        text = text.strip()
        text = re.sub(r',|"|\(|\)','', text)
        text = self.__normaliseDate(text)
        text= ' '.join(text.split())

        return text

    def __normaliseDate(self, dateString) -> str:

        if re.match(r'[0-9]{2}-\w+-[0-9]{4}', dateString) is not None:
            dateString = str(parse(dateString).date())

        return dateString

