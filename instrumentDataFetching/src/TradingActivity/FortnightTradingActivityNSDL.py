import logging
from pandas import DataFrame
import requests, pandas as pd
from bs4 import BeautifulSoup
from ..utils.HTTPClient import HTTPClient
from datetime import datetime


class FortnightTradingActivityNSDL:

    def __init__(self, config) -> None:
        self.config = config
        self.session = requests.session()
        self.httpClient = HTTPClient(self.config['nsdl']['host'],
                                     self.config['nsdl']['headers'])


    def fetch(self):

        fortnightlyData = DataFrame([])

        htmlText = self.httpClient.get(
                self.config['nsdl']['path.prefix'] + self.config['nsdl']['reportlist.path'], 
                isResponseTypeJson=False)
        soup = BeautifulSoup(htmlText, 'html.parser')

        reportsMetaData = self.__reportMetaData(soup, self.config['period.lookback'])
        fortnightlyData = self.__fortnightlyData(reportsMetaData)

        return fortnightlyData



    def __fortnightlyData(self, reportsMetaData):
        fortnightlyData = DataFrame([])

        for aReportMetaData in reportsMetaData:
            data = {}
            response = self.httpClient.get(
                    aReportMetaData[1], 
                    isResponseTypeJson=False)

            soup = BeautifulSoup(response, 'html.parser')
            soup = soup.find('div', {'id' : 'dvFortnightly'})
            table = soup.find_all('table', {})
            trows = table[0].find_all('tr')

            selectedRows = trows[3:len(trows)-1]
            for aRow in selectedRows:
                tdata = aRow.find_all('td')
                data['Date'] = datetime.strptime(aReportMetaData[0], '%b %d, %Y')
                data['timeframe'] = self.config['timeframe']
                data['entity'] = self.config['entity']
                data['sector'] = [ tdata[1].text ]
                data['investment'] = [ tdata[22].text.replace(',', '') ]
                data['auc'] = [ tdata[32].text.replace(',', '') ]

                fortnightlyData = pd.concat([fortnightlyData, 
                                             DataFrame.from_dict(data)])

            logging.debug(f'> fornightly data \n {fortnightlyData}')
        return fortnightlyData




    def __reportMetaData(self, soup, period):

        soup = soup.find('select', {'name' : 'ddlfortnighly', 'id' : 'ddlfortnighly'})
        reports = soup.find_all('option')

        reportsMetaData = []
        for aReport in reports:
            date = aReport.text
            path = self.config['nsdl']['path.prefix'] +  aReport['value'].replace('~', '')
            reportsMetaData.append((date, path))

        reportsMetaData = reportsMetaData[:period]
        logging.debug(f'> fornightly meta info data \n {reportsMetaData}')
        return reportsMetaData
