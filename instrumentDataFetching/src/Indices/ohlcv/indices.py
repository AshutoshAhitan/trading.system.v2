import abc
from multiprocessing import Pool

from ...Database.DatabaseFactory import DatabaseFactory
import logging

class Indices(abc.ABC):

	def __init__(self, config, dbConfigPath, symbolList) -> None:
		super().__init__()
		self.config = config
		self.dbConfigPath = dbConfigPath
		self.symbolList = symbolList

	@abc.abstractmethod
	def fetchData(self, symbol):
		pass

	def w_fetchData(self, args):
		index, exchange, symbol = args['index'], args['exchange'], args['symbol']
		try:
			ohlcv = self.fetchData(exchange, symbol)
			ohlcv['index'] = index
			DatabaseFactory.create(self.dbConfigPath).saveRecords(self.config['dest.table'],
														self.config['dest.table.primary.keys'],
														ohlcv)
			logging.info(f'{symbol} ohlcv data saved.')
			return 0, symbol, ''
		except Exception as e:
			print(e)
			return -1, symbol, e


	def fetch(self):

		args = self.config['indices.list']

		logging.debug(args)
		logging.info(f'Fetching data for {len(args)} symbols.')

		with Pool(1) as p:
			failedSymbols = p.map(self.w_fetchData, args)
			failedSymbols = [(symbol, reason) for status, symbol, reason in failedSymbols if status != 0]
			logging.info(failedSymbols)

