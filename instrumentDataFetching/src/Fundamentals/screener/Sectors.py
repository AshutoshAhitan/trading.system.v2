import logging
from bs4 import BeautifulSoup

import re

class Sectors():


    def __init__(self, scrapperConfig) -> None:

        self.cssSelector = scrapperConfig['css.selector']
        self.rootHtmlTag = scrapperConfig['root.html.tag']
        self.rootHtmlAttrId, self.rootHtmlAttrValue = scrapperConfig['root.html.attr'].split(':')


    def fetch(self, htmlData, symbol):
        sector = { 'sector' : '', 'industry' : ''}

        soup = BeautifulSoup(htmlData, 'html.parser')
        htmlElement = soup.find(self.rootHtmlTag, attrs= {self.rootHtmlAttrId : self.rootHtmlAttrValue})
        htmlElement = self.__sectorHtml(htmlElement)
        text = htmlElement.text.strip().replace('\n', '')

        logging.debug(f'> sectors defined for {symbol} : {text}')

        match = re.search(r'Sector:(?P<sector>.*)Industry:(?P<industry>.*)', text)
        if match is not None:
            sector['sector'] = match.groupdict()['sector'].strip()
            sector['industry'] = match.groupdict()['industry'].strip()
            logging.debug(f'> sectors :  {sector}')
        else:
            raise Exception(f'> error in fetching sectors for {symbol}')

        return sector


    def __sectorHtml(self, htmlElement):

        sectorHtml = None

        for selector in self.cssSelector:
            sectorHtml = htmlElement.select_one(selector)
            if sectorHtml is None: continue
            else: return sectorHtml

        return sectorHtml
