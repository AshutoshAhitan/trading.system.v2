from bs4 import BeautifulSoup
from .utils import parseScreenerTable
import logging

class AnnualResults():


    def __init__(self, scrapperConfig) -> None:

        self.config = scrapperConfig
        self.rootHtmlTag = scrapperConfig['root.html.tag']
        self.rootHtmlAttrId, self.rootHtmlAttrValue = scrapperConfig['root.html.attr'].split(':')
        self.tableHeaderSelector = scrapperConfig['table.header.css.selector']
        self.tableBodySelector = scrapperConfig['table.body.css.selector']


    def fetch(self, htmlData, symbol):
        annualResults = {}

        soup = BeautifulSoup(htmlData, 'html.parser')
        htmlElement = soup.find(self.rootHtmlTag, attrs= {self.rootHtmlAttrId : self.rootHtmlAttrValue})

        tableHeaderHtml = self.__tableHeaderHtml(htmlElement)
        logging.debug(tableHeaderHtml)
        tableBodyHtml = self.__tableBodyHtml(htmlElement)
        logging.debug(tableBodyHtml)

        results = parseScreenerTable(tableHeaderHtml, tableBodyHtml)
        for key in results.keys():
            if key in self.config['annual.results.relevant_keys']:
                annualResults[key] = results[key]

        return annualResults


    def __tableHeaderHtml(self, htmlElement):

        tableHeaderHtml = None

        for selector in self.tableHeaderSelector:
            tableHeaderHtml = htmlElement.select_one(selector)
            if tableHeaderHtml is None: continue
            else: return tableHeaderHtml

        return tableHeaderHtml


    def __tableBodyHtml(self, htmlElement):

        tableBodyHtml = None

        for selector in self.tableBodySelector:
            tableBodyHtml = htmlElement.select_one(selector)
            if tableBodyHtml is None: continue
            else: return tableBodyHtml

        return tableBodyHtml
