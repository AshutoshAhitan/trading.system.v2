import abc
from multiprocessing import Pool
from time import sleep
from ..Database.DatabaseFactory import DatabaseFactory
import logging

class OHLCV(abc.ABC):

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
			ohlcv = self.fetchData(symbol)
			DatabaseFactory.create(self.dbConfigPath).saveRecords(self.configuration['dest.table'],
														self.configuration['dest.table.primary.keys'],
														ohlcv)
			logging.info(f'{symbol} ohlcv data saved.')
			return 0, symbol, ''
		except Exception as e:
			print(e)
			return -1, symbol, e
		# finally:
			# sleep(10)



	def fetch(self):

		symbols = []
		if len(self.symbolList) == 0:
			symbols = DatabaseFactory.create(self.dbConfigPath) \
			.fetchRecords(tablename=self.symbolSrcTable,
			tableColumnFilter=self.symbolSrcTableColumnFilter,
			tableColumnSelect=[ self.symbolSrcTableColumnSelect ])[self.symbolSrcTableColumnSelect].to_list()
		else:
			symbols = self.symbolList
			logging.debug(symbols)

		logging.info(f'Fetching data for {len(symbols)} symbols.')

		with Pool(2) as p:
			failedSymbols = p.map(self.w_fetchData, symbols)
			failedSymbols = [(symbol, reason) for status, symbol, reason in failedSymbols if status != 0]
			logging.info(failedSymbols)
