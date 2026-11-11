import abc
from multiprocessing import Pool

from ...Database.DatabaseFactory import DatabaseFactory
import logging

class WeeklyStrikePrice(abc.ABC):

	def __init__(self, config, dbConfigPath) -> None:
		super().__init__()
		self.config = config
		self.dbConfigPath = dbConfigPath
		self.indicesList = self.config['indices.list']
		self.count = 0
		self.symbolCount = 0

	@abc.abstractmethod
	def fetchData(self, symbol, interval, period):
		pass

	@abc.abstractmethod
	def instruments(self):
		pass


	def __strikeSymbol(self, strikeList, strikePrice):
		row = strikeList[strikeList['strike'] == strikePrice]
		symbols = []
		if not row.empty:
			for index, data in row.iterrows():
				symbols.append((data['tradingsymbol'], data['expiry'], data['strike'], data['instrument_type']))
		return symbols


	def __weeklyExpiryStrikes(self):
		instruments = self.instruments()
		logging.debug(f'instruments fetched: {instruments}')
		weeklyExpiry = instruments['expiry'].sort_values().unique()[0]
		logging.debug(f"Weekly Expiry Date: {weeklyExpiry}")

		instruments = instruments[instruments['expiry'] == weeklyExpiry]
		instruments = instruments.sort_values(by='strike', ascending=True)
		logging.debug(instruments[['instrument_token', 'tradingsymbol', 'expiry', 'strike']])

		return instruments


	def __getNearestStrikes(self, ltp):
		nearest_strike = round(ltp / 50) * 50
		strikes_down = [nearest_strike - 5*50,
						nearest_strike - 4*50,
				  		nearest_strike - 3*50, 
						nearest_strike - 2*50, 
						nearest_strike - 50]

		strikes_up = [nearest_strike + 50, 
						nearest_strike + 2*50, 
						nearest_strike + 3*50, 
						nearest_strike + 4*50,
						nearest_strike + 5*50]

		strikes = strikes_down + [nearest_strike] + strikes_up
		return strikes


	def w_fetchData(self, index, symbol, strikeSymbol):
		try:
			# index, symbol, strikeData = args
			strikeSymbol, expiry, strike, instrument_type = strikeSymbol

			# Fetch and save 1m data
			ohlcv_1m = self.fetchData(strikeSymbol, '1m', '7d', 'NFO')
			ohlcv_1m['index'] = index
			ohlcv_1m['Symbol'] = strikeSymbol
			ohlcv_1m['strikePrice'] = strike
			ohlcv_1m['expiry'] = expiry
			ohlcv_1m['instrumentType'] = instrument_type
			DatabaseFactory.create(self.dbConfigPath).saveRecords(self.config['dest.table'],
														self.config['dest.table.primary.keys'],
														ohlcv_1m)
			logging.info(f'{strikeSymbol} 1m ohlcv data saved.')

			# Fetch and save 3m data
			ohlcv_3m = self.fetchData(strikeSymbol, '3m', '7d', 'NFO')
			ohlcv_3m['index'] = index
			ohlcv_3m['Symbol'] = strikeSymbol
			ohlcv_3m['strikePrice'] = strike
			ohlcv_3m['expiry'] = expiry
			ohlcv_3m['instrumentType'] = instrument_type
			DatabaseFactory.create(self.dbConfigPath).saveRecords(self.config['dest.table'],
														self.config['dest.table.primary.keys'],
														ohlcv_3m)
			logging.info(f'{strikeSymbol} 3m ohlcv data saved.')

			return 0, strikeSymbol, ''
		except Exception as e:
			print(e)
			return -1, strikeSymbol, e


	def __multiProcessFetch(self, index, symbol, strikeSymbols):
		with Pool(1) as p:
			# Prepare arguments as a list of tuples for starmap
			args = [(index, symbol, s) for s in strikeSymbols]
			failedSymbols = p.starmap(self.w_fetchData, args)
			failedSymbols = [(symbol, reason) for status, symbol, reason in failedSymbols if status != 0]
			return failedSymbols


	def fetch(self):
		for record in self.indicesList:
			index = record['index']; exchange = record['exchange']; symbol = record['symbol']

			logging.info(f'Fetching strike price data for index: {index}; exchange: {exchange}; symbol: {symbol}')

			weeklyExpiryStrikes = self.__weeklyExpiryStrikes()

			indexOhlcv = self.fetchData(symbol, '1m', '7d', exchange)
			indexCloseValues = indexOhlcv['Close'].unique()
			logging.info(f'unique close values for index: {len(indexCloseValues)}')

			strikeSymbol = []
			for ltp in indexCloseValues:
				strikes = self.__getNearestStrikes(ltp)
				for strike in strikes:
					strikeSymbol = strikeSymbol + self.__strikeSymbol(weeklyExpiryStrikes, strike)

			strikeSymbol = list(set(strikeSymbol))
			logging.info(f'Total unique strike symbols to be fetched: {len(strikeSymbol)}')
			logging.info(f'strike symbols:\n {[symbol for symbol, expiry, strike, instrument_type in strikeSymbol]}')	
			self.symbolCount = len(strikeSymbol)

			if None in strikeSymbol:
				raise Exception('None found for strike symbol')
			

			failedSymbols = self.__multiProcessFetch(index, symbol, strikeSymbol)

			logging.info('Strike Price Data Fetching Completed.')
			if failedSymbols:
				logging.error(f'Failed Symbols: {failedSymbols}')