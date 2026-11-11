from bs4 import BeautifulSoup
from pandas.core.frame import DataFrame
from ..utils.communication import Communication
import pandas as pd, logging
from datetime import datetime

class DailyTradingAcitvityMoneyControl():

    def __init__(self, config: dict) -> None:
        self.config = config

        self.communication = Communication(self.config['moneycontrol']['url'])
        self.headers    = self.config['moneycontrol']['headers']
        self.payload    = self.config['moneycontrol']['payload']
        self.method     = self.config['moneycontrol']['method']
        self.path  = self.config['moneycontrol']['path']


    def fetch(self) -> DataFrame:

        tradingActivityDf = DataFrame([])
        dailyTradingActivityDf = DataFrame([])
        monthlyTradingActivityDf = DataFrame([])

        htmlData    = self.communication.fetch(self.method, self.path, self.payload, self.headers, cookie='', responseType='text')
        soup        = BeautifulSoup(htmlData, 'html.parser')

        table = self.__getTradingAcitvityTable(soup, tag='div', attrs = {'class' : 'clearfix MB20'})
        dailyTradingActivityDf = self.__extractTradingDatafromTable(table[1], timeFormat='%d-%b-%Y')
        dailyTradingActivityDf['timeframe'] = '1d'
        dailyTradingActivityDf['entity'] = self.config['entity']
        logging.debug(dailyTradingActivityDf)

        table = self.__getTradingAcitvityTable(soup, tag='section', attrs = {'class' : 'prevfidi_sec'})
        monthlyTradingActivityDf = self.__extractTradingDatafromTable(table[1], timeFormat='%B %Y')
        monthlyTradingActivityDf['timeframe'] = '1mo'
        monthlyTradingActivityDf['entity'] = self.config['entity']
        logging.debug(monthlyTradingActivityDf)

        tradingActivityDf = pd.concat([dailyTradingActivityDf, monthlyTradingActivityDf])

        return tradingActivityDf


    def __getTradingAcitvityTable(self, soup, tag, attrs):

        table = soup.find(tag, attrs)
        table = table.find_all('tbody')
        return table


    def __extractTradingDatafromTable(self, tradingAcitivityTable, timeFormat):
        tradingActivity = DataFrame([])

        for aRow in tradingAcitivityTable.find_all('tr'):
            columns = aRow.find_all('td')
            date = columns[0].find('span', attrs={'class' : 'mob-hide'}).text.strip()
            date = datetime.strptime(date, timeFormat)

            fiiBuyValue   = columns[1].text.strip().replace(',', '')
            fiiSellValue  = columns[2].text.strip().replace(',', '')
            fiiNetValue   = columns[3].text.strip().replace(',', '')
            diiBuyValue   = columns[4].text.strip().replace(',', '')
            diiSellValue  = columns[5].text.strip().replace(',', '')
            diiNetValue   = columns[6].text.strip().replace(',', '')

            tradingActivity = pd.concat([tradingActivity, DataFrame(data = {
                'Date' : [date],
                'FIIBuyValue' : [fiiBuyValue],
                'FIISellValue' : [fiiSellValue],
                'FIINetValue' : [fiiNetValue],
                'DIIBuyValue' : [diiBuyValue],
                'DIISellValue' : [diiSellValue],
                'DIINetValue' : [diiNetValue]
            })])

        return tradingActivity
