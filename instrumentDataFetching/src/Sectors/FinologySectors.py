import logging, time
from ..utils.communication import Communication
from bs4 import BeautifulSoup
import pandas as pd
from .Sectors import Sectors
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options



class FinologySectors(Sectors):

    def __init__(self, config, database) -> None:
        print(config)
        super().__init__(config, database)
        # config = config[config['src']]

        self.config = config
        self.industryConfig = self.config['industry']
        self.scraper = self.industryConfig['scraper']
        self.headersRename = self.scraper['headers.rename']
        self.database = database

        options = Options()
        if self.scraper['headless'] == True: 
            options.add_argument('--headless=new')
        self.driver = webdriver.Chrome(options=options)

    def fetch(self):

        industries = self.__industries()
        stocks = self.__w_stocks(industries)
        logging.info(stocks)

        return stocks

    def __industries(self):

        industries = pd.DataFrame([])

        communication = Communication(self.industryConfig['host'])
        htmlData      = communication.fetch(self.industryConfig['method'], self.industryConfig['path'],
                                            self.industryConfig['payload'], 
                                            self.industryConfig['headers'], cookie='', responseType='text')

        soup = BeautifulSoup(htmlData, 'html.parser')
        industriesElements = soup.find_all('div', attrs={'class' : 'row filterlist'})
        industriesElements = industriesElements[0].find_all('div', attrs={'class' : 'col-12 col-md-3'})

        for anIndustryElement in industriesElements:
            logging.debug('\n>> ------ extracting industry information --------')
            logging.debug(anIndustryElement)

            industryName = self.__industryName(anIndustryElement)
            industryDescription = self.__industryDescription(anIndustryElement)
            industryDetailsLink = self.__industryDetailsLink(anIndustryElement)

            df = pd.DataFrame(data={
                'industry' : [industryName],
                'industry.description' : [industryDescription],
                'industry.link' : [industryDetailsLink]
            })
            industries = pd.concat([industries, df])


        logging.info(industries)
        return industries



    def __industryName(self, element):
        return (element.find('h4', attrs={'class' : 'mb-0 mt-3 industry'})).text

    def __industryDescription(self, element):
        return (element.find('p', attrs={'class' : 'compinfo sector mb-3 mt-2 descp'})).text.strip()

    def __industryDetailsLink(self, element):
        return element.find('a',attrs={'class' : 'btn btn-sm btn-primary align-self-center'}, href=True)['href']


    def __w_stocks(self, industries):
        stocksDf = pd.DataFrame([])

        for idx, anIndustry in industries.iterrows():
            logging.info(f'\n>> ---------------- scraping list of stocks for {anIndustry.industry} industry --------------------')
            time.sleep(3)
            stocks = self.__stocks(anIndustry['industry.link'], anIndustry.industry)
            stocksDf = pd.concat([stocksDf, pd.DataFrame.from_records(stocks)])

        return stocksDf



    def __stocks(self, industryLink, industryName):

        url = f"https://{self.industryConfig['host']}{industryLink}"
        logging.debug(url)

        self.driver.get(url)
        element = WebDriverWait(self.driver, self.scraper['poll_css_selector_period']).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR,
                    self.scraper['poll_css_selector'])))

        page_source = self.driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')

        soup = soup.find('div', attrs={'id' : self.scraper['div']})
        soup = soup.find('table', attrs={'id' : self.scraper['table']})

        tdata = self.__extractTableData(soup, industryLink, industryName)
        stocks = pd.DataFrame.from_records(data=tdata)
        stocks['symbol'] = self.__stockSymbol(stocks['company.link'])

        logging.info(stocks)

        return stocks

    def __stockSymbol(self, stockLinkList):
        stocksSymbols = stockLinkList.apply(lambda link: link.split('/')[-1])
        return stocksSymbols

    def __extractTableData(self, soup, industryLink, industryName):

        theaders = self.__w_tableHeaders(soup)
        trows = self.__tableData(soup)

        tdata = []
        for row in trows:
            rdata = {}
            for idx, column in enumerate(row):
                rdata.update({ f'{theaders[idx]}.link' : self.industryConfig['host'] + column[0],
                              f'{theaders[idx]}' : column[1] })
            rdata.update({'industry.link' : self.industryConfig['host'] + industryLink, 'industry' : industryName})
            tdata.append(rdata)

        logging.debug(f'---------------- table data -------------------')
        logging.debug(tdata)

        return tdata;


    def __w_tableHeaders(self, soup):

        theaders = self.__tableHeaders(soup)
        renamedHeaders = self.__renameHeaders(theaders)

        return renamedHeaders


    def __renameHeaders(self, theaders):

        renamedHeader = []
        for header in theaders:
            if header in self.headersRename.keys():
                renamedHeader.append(self.headersRename[header])
            else:
                renamedHeader.append(header)

        logging.debug(f'renamed headers -> {renamedHeader}')

        return renamedHeader


    def __tableHeaders(self, soup):

        trow = (soup.find('thead')).find('tr')
        theaders = trow.find_all('div')
        headers = [theader.text for theader in theaders if len(theader) != 0]

        logging.debug(f'headers -> {headers}')

        return headers


    def __tableData(self, soup):

        tdata = []
        tableRows = (soup.find('tbody')).find_all('tr')
        for row in tableRows:
            data = []
            tcolums = row.find_all('td')
            for tcolumn in tcolums: 
                link, value = self.__tableColumn(tcolumn)
                data.append((link, value))

            tdata.append(data)

        logging.debug(f'table data -> {tdata}')

        return tdata


    def __tableColumn(self, tcolumn):
        link = ''; value = ''

        if tcolumn.find('a', href=True) is not None: 
            link = tcolumn.find('a', href=True)['href']
        value = tcolumn.text

        return link, value









