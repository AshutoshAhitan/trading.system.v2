import json, logging
from .EarningsCalender import EarningsCalender
from ...utils.HTTPClient import HTTPClient

from ...Database.DatabaseFactory import DatabaseFactory
from pandas import DataFrame
from multiprocessing import Pool
from datetime import date

class YahooFinance(object):

    def __init__(self, config, dbConfigPath, symbolList) -> None:
        self.config = config
        self.dbConfigPath = dbConfigPath
        self.symbolList = symbolList

        self.httpClient = HTTPClient(self.config['yfinance']['host'],
                                     self.config['yfinance']['headers'])

        self.earningsCalender = EarningsCalender(self.config['yfinance']['earnings.calender']['scrapper'])

        self.symbolSrcTable = config['symbol.src.table']
        self.symbolSrcTableColumnFilter = config['symbol.src.table.column.filter']
        self.symbolSrcTableColumnSelect = config['symbol.src.table.column.select']

        self.symbols = self.__symbolList(self.symbolList)


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

        try:
            logging.info(f'______________ Fetching Earnings Calender For {symbol} ________________')

            # fetch quarterly results from database
            column = [self.config['yfinance']['quarterly.results']['src.table.column.select']]

            quarterlyResults = DatabaseFactory.create(self.dbConfigPath).fetchRecords(
                self.config['yfinance']['quarterly.results']['src.table'],
                {'symbol' : symbol},
                column
            )[column].iloc[0]
            logging.info(f'quarterly results : {quarterlyResults}')

            earningsCalender = self.earningsCalender.fetch(quarterlyResults, f'{symbol}.NS')
            logging.debug(f'earnings calender : {earningsCalender}')

            DatabaseFactory.create(self.dbConfigPath).saveRecords(self.config['yfinance']['dest.table'],
														self.config['yfinance']['dest.table.primary.keys'],
														earningsCalender,
														self.config['yfinance']['dest.table.truncate'])

            return 0, symbol, ''
        except Exception as e:
            return -1, symbol, e



    def fetch(self):

        # with Pool(5) as p:
        #     failedSymbols = p.map(self.fetch_pp, self.symbols)
        #     failedSymbols = [(symbol, reason) for status, symbol, reason in failedSymbols if status != 0]
        #     logging.info(failedSymbols)

        failedSymbols = []
        for symbol in self.symbols:
            result = self.fetch_pp(symbol)
            print(result)
            if result[0] != 0:
                failedSymbols.append([(symbol, result[2])])
        
        logging.info(failedSymbols)



