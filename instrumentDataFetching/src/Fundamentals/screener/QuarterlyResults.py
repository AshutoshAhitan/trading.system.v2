from bs4 import BeautifulSoup
from .utils import parseScreenerTable

class QuarterlyResults():


    def __init__(self, scrapperConfig) -> None:

        self.config = scrapperConfig
        self.rootHtmlTag = scrapperConfig['root.html.tag']
        self.rootHtmlAttrId, self.rootHtmlAttrValue = scrapperConfig['root.html.attr'].split(':')
        self.tableHeaderSelector = scrapperConfig['table.header.css.selector']
        self.tableBodySelector = scrapperConfig['table.body.css.selector']


    def fetch(self, htmlData, symbol):
        quarterlyResults = {}

        soup = BeautifulSoup(htmlData, 'html.parser')
        htmlElement = soup.find(self.rootHtmlTag, attrs= {self.rootHtmlAttrId : self.rootHtmlAttrValue})

        tableHeaderHtml = self.__tableHeaderHtml(htmlElement)
        tableBodyHtml = self.__tableBodyHtml(htmlElement)

        results = parseScreenerTable(tableHeaderHtml, tableBodyHtml)
        for key in results.keys():
            if key in self.config['quarterly.results.relevant_keys']:
                quarterlyResults[key] = results[key]

        return quarterlyResults


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
