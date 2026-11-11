import json
from .MarketCap import MarketCap
from .IndustryInfo import IndustryInfo
from .SecurityInfo import SecurityInfo
from .EarningsCalender import EarningsCalender

import logging
from ...Database.DatabaseFactory import DatabaseFactory
from pandas import DataFrame
from multiprocessing import Pool
from datetime import date

class NSE(object):

    def __init__(self, config, dbConfigPath, symbolList) -> None:
        self.config = config
        self.dbConfigPath = dbConfigPath
        self.symbolList = symbolList

        self.marketCap = MarketCap(self.config['nse'])
        self.securityInfo = SecurityInfo(self.config['nse'])
        self.industryInfo = IndustryInfo(self.config['nse'])
        self.earningsCalender = EarningsCalender(self.config['nse'])

        self.symbolSrcTable = config['symbol.src.table']
        self.symbolSrcTableColumnFilter = config['symbol.src.table.column.filter']
        self.symbolSrcTableColumnSelect = config['symbol.src.table.column.select']

        self.symbols = self.__symbolList(symbolList)


    def __symbolList(self, symbolList):

        symbols = []
        if len(symbolList) == 0:

            database = DatabaseFactory.create(self.dbConfigPath)

            symbols = database.fetchRecords(tablename=self.symbolSrcTable,
            tableColumnFilter=self.symbolSrcTableColumnFilter,
            tableColumnSelect=[ self.symbolSrcTableColumnSelect ],
            )[self.symbolSrcTableColumnSelect].to_list()

        else:
            symbols = symbolList

        symbols = list(set(symbols))
        logging.debug(symbols)

        return symbols




    def fetch_pp(self, symbol):

        fundamentals = DataFrame([])
        marketCap = {}; securityInfo = {}; industryInfo = {};
        earningsCalender = []
        data = {}

        data['symbol'] = [symbol]
        try:

            if self.config['fundamentals']['marketCap.fetch'] is True:
                marketCap = self.marketCap.fetch(symbol)
                data['marketCap'] = [json.dumps(marketCap)]

            if self.config['fundamentals']['securityInfo.fetch'] is True:
                securityInfo = self.securityInfo.fetch(symbol)
                data['securityInfo'] = [json.dumps(securityInfo)]

            if self.config['fundamentals']['industryInfo.fetch'] is True:
                industryInfo = self.industryInfo.fetch(symbol)
                data['industryInfo'] = [json.dumps(industryInfo)]

            if self.config['fundamentals']['earningsCalender.fetch'] is True:
                earningsCalender = self.earningsCalender.fetch(symbol)
                data['earningsCalender'] = [json.dumps(earningsCalender)]

            fundamentals = DataFrame.from_dict(data)

            logging.info(fundamentals)

            DatabaseFactory.create(self.dbConfigPath).saveRecords(self.config['dest.table'],
														self.config['dest.table.primary.keys'],
														fundamentals,
														self.config['dest.table.truncate'])

            return 0, symbol, ''
        except Exception as e:
            return -1, symbol, e



    def fetch(self):

        with Pool(5) as p:
            failedSymbols = p.map(self.fetch_pp, self.symbols)
            failedSymbols = [(symbol, reason) for status, symbol, reason in failedSymbols if status != 0]
            logging.info(failedSymbols)
