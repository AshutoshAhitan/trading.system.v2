import abc
from multiprocessing import Pool
from ..Database.DatabaseFactory import DatabaseFactory
import logging

class Liquidity(abc.ABC):

	def __init__(self, config, dbConfigPath, symbolList) -> None:
		super().__init__()
		self.configuration = config
		self.dbConfigPath = dbConfigPath
		self.symbolList = symbolList
		self.symbolSrcTable = config['symbol.src.table']
		self.symbolSrcTableColumnFilter = config['symbol.src.table.column.filter']
		self.symbolSrcTableColumnSelect = config['symbol.src.table.column.select']

	@abc.abstractmethod
	def fetchData(self, symbol):
		pass

	def w_fetchData(self, symbol):
		try:
			liquidity = self.fetchData(symbol)
			DatabaseFactory.create(self.dbConfigPath).saveRecords(self.configuration['dest.table'],
														self.configuration['dest.table.primary.keys'],
														liquidity)
			logging.info(f'{symbol} liquidity data saved.')
			return 0, symbol, ''
		except Exception as e:
			print(e)
			return -1, symbol, e



	def fetch(self):

		symbols = []
		instrumentTokens = []

		database = DatabaseFactory.create(self.dbConfigPath)
		if len(self.symbolList) == 0:
			instrumentTokens = database \
			.fetchRecords(tablename=self.symbolSrcTable,
			tableColumnFilter=self.symbolSrcTableColumnFilter,
			tableColumnSelect=[ self.symbolSrcTableColumnSelect ])[self.symbolSrcTableColumnSelect].to_list()
		else:
			symbols = self.symbolList
			for symbol in symbols:
				instrumentToken = database.fetchRecords(tablename=self.symbolSrcTable,
				tableColumnFilter={'symbol': {
            		"op": "=",
            		"value": symbol
        		}},
				tableColumnSelect=[self.symbolSrcTableColumnSelect])[self.symbolSrcTableColumnSelect].to_list()

				logging.debug(f'Instrument token for {symbol} is {instrumentToken[0]}')
				instrumentTokens.append(instrumentToken[0])

		with Pool(1) as p:
			failedSymbols = p.map(self.w_fetchData, instrumentTokens)
			failedSymbols = [(symbol, reason) for status, symbol, reason in failedSymbols if status != 0]
			logging.info(failedSymbols)
