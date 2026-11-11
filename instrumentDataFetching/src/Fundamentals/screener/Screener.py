import json, logging, time, traceback
from .AnnualResults import AnnualResults
from .QuarterlyResults import QuarterlyResults
from .ShareholdingPattern import ShareholdingPattern
from .Sectors import Sectors
from ...utils.HTTPClient import HTTPClient


from ...Database.DatabaseFactory import DatabaseFactory
from pandas import DataFrame
from multiprocessing import Pool
from datetime import date

class Screener(object):

    def __init__(self, config, dbConfigPath, symbolList) -> None:
        self.config = config
        self.dbConfigPath = dbConfigPath
        self.symbolList = symbolList

        self.annualResults = AnnualResults(self.config['screener']['scrapper.annualResults'])
        self.quarterlyResults = QuarterlyResults(self.config['screener']['scrapper.quarterlyResults'])
        self.shareholdingPattern = ShareholdingPattern(self.config['screener']['scrapper.shareholdingPattern'])
        self.sectors = Sectors(self.config['screener']['scrapper.sector'])

        self.symbolSrcTable = config['symbol.src.table']
        self.symbolSrcTableColumnFilter = config['symbol.src.table.column.filter']
        self.symbolSrcTableColumnSelect = config['symbol.src.table.column.select']

        self.htttpClient = HTTPClient(self.config['screener']['host'],
                                     self.config['screener']['headers'])

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
        time.sleep(10)
        logging.info(f'fetching fundamentals for {symbol} from screener')

        fundamentals = DataFrame([])
        annualResults = {}; quarterlyResults = {}; shareholdingPattern = {}; sectors = {}
        try:

            path = self.config['screener']['equity.fundamentals'].replace('{symbol}', symbol)
            html = self.htttpClient.get(path, isResponseTypeJson=False)

            annualResults = self.annualResults.fetch(html, symbol)
            logging.debug(f'> annualResults : {annualResults}')

            quarterlyResults = self.quarterlyResults.fetch(html, symbol)
            logging.debug(f'> quarterlyResults : {quarterlyResults}')

            shareholdingPattern = self.shareholdingPattern.fetch(html, symbol)
            logging.debug(f'> shareholdingPattern : {shareholdingPattern}')

            sectors = self.sectors.fetch(html, symbol)
            logging.debug(f'> sectors : {sectors}')

            fundamentals = DataFrame.from_dict(data={
                'symbol' : [symbol],
                'annualResults' : [json.dumps(annualResults)],
                'quarterlyResults' : [json.dumps(quarterlyResults)],
                'shareholdingPattern' : [json.dumps(shareholdingPattern)],
                'sectors' : [json.dumps(sectors)]
                })

            DatabaseFactory.create(self.dbConfigPath).saveRecords(self.config['dest.table'],
                                                        self.config['dest.table.primary.keys'],
                                                        fundamentals,
                                                        self.config['dest.table.truncate'])

            return 0, symbol, ''
        except Exception as e:
            print(e)
            print(traceback.format_exc())
            return -1, symbol, e



    def fetch(self):

        with Pool(1) as p:
            failedSymbols = p.map(self.fetch_pp, self.symbols)
            failedSymbols = [(symbol, reason) for status, symbol, reason in failedSymbols if status != 0]
            logging.info(failedSymbols)
