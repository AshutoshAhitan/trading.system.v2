from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from .utils import convert_to_datetime, get_indices, get_financial_quarter
import logging, pandas as pd

class EarningsCalender:

    def __init__(self, scrapperConfig) -> None:
        chrome_options = Options()
        chrome_options.add_experimental_option(
            "prefs",
            { 'profile.managed_default_content_settings.javascript':2 })

        self.driver = webdriver.Chrome(options=chrome_options)

        self.rootHtmlTag = scrapperConfig['root.html.tag']
        self.rootHtmlAttrId, self.rootHtmlAttrValue = scrapperConfig['root.html.attr'].split(':')
        self.tableHeaderSelector = scrapperConfig['table.header.css.selector']
        self.tableBodySelector = scrapperConfig['table.body.css.selector']


    def fetch(self, quarterlyResults, symbol):

        self.driver.get(f"https://finance.yahoo.com/calendar/earnings/?symbol={symbol}")
        page_source = self.driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')

        soup = soup.find('div', attrs={'id' : 'cal-res-table'})
        table = soup.find('table', attrs={'class' : 'W(100%)'})

        soup = table.find('tbody')
        soup = table.find_all('tr')

        earnings = self.__extractEarningsData(soup)
        earnings = self.__addEarningsDateToQuarterlyResults(quarterlyResults, earnings)
        earnings = pd.DataFrame(earnings)
        logging.info(f'earnings : {earnings}')

        return earnings


    def __addEarningsDateToQuarterlyResults(self, quarterlyResults, earnings):
        earningsDate = { 'Date' : [], 'data' : []}

        earningsQuarters = earnings['quarter']
        logging.debug(f'earnings quarter : {earningsQuarters}')
        earningsDate['Date'] = earningsQuarters

        earningsDates = earnings['datetime']
        logging.debug(f'earnings dates : {earningsDate}')
        earningsDate['data'] = earningsDates

        quarterlyResults['earningsDates'] = earningsDates
        logging.debug(f'quarterly results after adding dates : {quarterlyResults}')

        return quarterlyResults


    def __extractEarningsData(self, soup):

        earnings = {'symbol' : [], 'company' : [], 'datetime' : [],
            'eps.estimate' : [], 'eps.actual' : [], 'surprise%' : []}
        columns = list(earnings.keys())

        for row in soup:
            tableData = row.find_all('td')
            for idx, data in enumerate(tableData):
                if idx == 2:
                    earnings[columns[idx]].append(convert_to_datetime(data.text))
                else:
                    earnings[columns[idx]].append(data.text)

        logging.debug(f'earnings : {earnings}')

        min_date = min(earnings['datetime'])
        logging.debug(f'minimum date : {min_date}')
        min_date_index = earnings['datetime'].index(min_date)
        logging.debug(f'minimum date index : {min_date_index}')

        company = earnings['company'][min_date_index]
        logging.debug(f'company name : {company}')
        indices = get_indices(earnings['company'], company)
        logging.debug(f'company name indices : {indices}')

        earnings_filtered = {'symbol' : [], 'company' : [], 'datetime' : [], 
            'quarter' : [],
            'eps.estimate' : [], 'eps.actual' : [], 'surprise%' : []}

        for column in columns:
            for idx in indices:
                earnings_filtered[column].append(earnings[column][idx])

        for idx, datetime in enumerate(earnings_filtered['datetime']):
            earnings_filtered['datetime'][idx] = str(datetime)

        for datetime in earnings_filtered['datetime']:
            earnings_filtered['quarter'].append(get_financial_quarter(datetime))

        logging.debug(f'earnings after cleanup : {earnings_filtered}')

        return earnings_filtered

