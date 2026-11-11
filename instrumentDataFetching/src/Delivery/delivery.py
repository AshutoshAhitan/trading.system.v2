import abc
from multiprocessing import Pool
from pandas.core.api import DataFrame
from ..Database.DatabaseFactory import DatabaseFactory
import logging

class Delivery(abc.ABC):

	def __init__(self, config, dbConfigPath, symbolList) -> None:
		super().__init__()
		self.configuration = config
		self.dbConfigPath = dbConfigPath
		self.symbolList = symbolList
		self.symbolSrcTable = config['symbol.src.table']
		self.symbolSrcTableColumnFilter = config['symbol.src.table.column.filter']
		self.symbolSrcTableColumnSelect = config['symbol.src.table.column.select']

	@abc.abstractmethod
	def fetchData(self, symbol) -> DataFrame:
		pass

	def w_fetchData(self, symbol):
		try:
			ohlcv = self.fetchData(symbol)
			logging.info(ohlcv)
			DatabaseFactory.create(self.dbConfigPath).saveRecords(self.configuration['dest.table'],
														self.configuration['dest.table.primary.keys'],
														ohlcv)
			logging.info(f'{symbol} ohlcv data saved.')
			return 0, symbol, ''
		except Exception as e:
			print(e)
			return -1, symbol, type(e)


	def fetch(self):

		symbols = []
		if len(self.symbolList) == 0:
			symbols = DatabaseFactory.create(self.dbConfigPath) \
			.fetchRecords(tablename=self.symbolSrcTable,
			tableColumnFilter=self.symbolSrcTableColumnFilter,
			tableColumnSelect=[ self.symbolSrcTableColumnSelect ])[self.symbolSrcTableColumnSelect].to_list()
			logging.debug(symbols)
		else:
			symbols = self.symbolList
			logging.debug(symbols)

		with Pool(2) as p:
			failedSymbols = p.map(self.w_fetchData, symbols)
			failedSymbols = [(symbol, reason) for status, symbol, reason in failedSymbols if status != 0]
			logging.info(failedSymbols)
