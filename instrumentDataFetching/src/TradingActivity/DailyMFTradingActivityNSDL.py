import logging
from pandas import DataFrame
import requests, pandas as pd
from bs4 import BeautifulSoup
from ..utils.HTTPClient import HTTPClient
from datetime import datetime

class DailyMFTradingActivityNSDL:

    def __init__(self, config) -> None:
        self.config = config
        self.session = requests.session()
        self.httpClient = HTTPClient(self.config['sebi']['host'],
                                     self.config['sebi']['headers'])

    def fetch(self):

        tradingActivityData = DataFrame([])

        htmlText = self.httpClient.get(
                self.config['sebi']['path'], 
                isResponseTypeJson=False)
        soup = BeautifulSoup(htmlText, 'html.parser')

        tradingActivityData = self.__dailyTradingActivity(soup)

        return tradingActivityData


    def __dailyTradingActivity(self, soup):

        soup = soup.find('table')
        soup = soup.find('tbody')
        rows = soup.find_all('tr')
        rows = rows[:-2]

        tradingActivityData = pd.DataFrame([])
        for idx, aRow in enumerate(rows):
            data = {}
            if idx % 2 == 0:
                tdata = aRow.find_all('td')
                if tdata[0].text.lower() == 'total': continue 
                data['Date']        = datetime.strptime(tdata[0].text, '%d %b, %Y')
                data['BuyValue']    = [ tdata[2].text ]
                data['SellValue']   = [ tdata[3].text ]
                data['NetValue']    = [ self.__convertToSign(tdata[4].text) ]
                data['entity']      = [ self.config['entity'] ]
                data['timeframe']      = [ self.config['timeframe'] ]

                tradingActivityData = pd.concat([tradingActivityData, 
                                         pd.DataFrame.from_dict(data)])

        logging.debug(f'> daily mutual fund trading activity \n {tradingActivityData}')
        return tradingActivityData

    def __convertToSign(self, token):

        number = token
        if token[0] == '(':
            number = -1 * float(token[1:-1])
            logging.debug(f'> converted {token} to numeric type {number}')

        return number


