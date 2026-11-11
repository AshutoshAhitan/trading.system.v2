import logging, time
from ..utils.communication import Communication
from bs4 import BeautifulSoup
import pandas as pd
from .Sectors import Sectors


class MoneyControlSectors(Sectors):

    def __init__(self, config) -> None:
        super().__init__(config)
        config = config[config['src']]
        self.config = config
        self.sectorConfig = self.config['sector']
        self.industryConfig = self.config['industry']

    def fetch(self):
        return self.__sector()


    def __sector(self):
        sectorsData = pd.DataFrame([])

        communication = Communication(self.sectorConfig['host'])
        htmlData      = communication.fetch(self.sectorConfig['method'], self.sectorConfig['path'],
                                               self.sectorConfig['payload'], self.sectorConfig['headers'], cookie='', responseType='text')
        soup        = BeautifulSoup(htmlData, 'html.parser')
        sectors = soup.find_all('div', attrs={'class' : 'lftmenu'})[0].find_all('li')

        for aSector in sectors:
            href = aSector.find('a', href=True)
            time.sleep(1)
            if href is not None:
                industryData = self.__getIndustry(href.get("href"))
                industryData['sector'] = href.text
                sectorsData = pd.concat([sectorsData, industryData])
                logging.debug(sectorsData)


        return sectorsData



    def __getIndustry(self, path):

        industry = pd.DataFrame()

        communication = Communication(self.industryConfig['host'])
        htmlData      = communication.fetch(self.industryConfig['method'], path,
                                            self.industryConfig['payload'], 
                                            self.industryConfig['headers'], cookie='', responseType='text')

        soup        = BeautifulSoup(htmlData, 'html.parser')
        industryTable = soup.find('table', attrs={'class' : 'tbldata14 bdrtpg'})
        if industryTable is None:
            return industry

        industryRows = industryTable.find_all('tr')

        for aRow in industryRows:
            columns = aRow.find_all('td')
            if columns:
                if columns[0].text == 'No Data Available':
                    return industry

                df = pd.DataFrame(data={
                    'companyLink' : [columns[0].find_all('a', href=True)[0]['href']],
                    'companyName' : [ columns[0].text ],
                    'industry' : [ columns[1].text ],
                    'marketCap' : [ columns[5].text.replace(',', '') ]
                    })
                industry = pd.concat([industry, df])

        return industry


    def getCompanyDetails(self, path):

        communication = Communication(self.industryConfig['host'])
        htmlData      = communication.fetch(self.industryConfig['method'], path,
                                            self.industryConfig['payload'], 
                                            self.industryConfig['headers'], cookie='', responseType='text')

        soup        = BeautifulSoup(htmlData, 'html.parser')
        print(soup)




