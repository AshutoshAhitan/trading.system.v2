from pandas.core.frame import DataFrame
from ..Database.DatabaseFactory import DatabaseFactory
from ..utils.utils import readConfigFile
from multiprocessing import Pool
import logging, traceback

class MarketBreadth():

	def __init__(self, config, dbConfigPath, symbolList) -> None:

		self.configuration = readConfigFile(config)
		self.dbConfigPath = dbConfigPath
		self.symbolSrcTable = self.configuration['symbol.src.table']
		self.symbolSrcTableColumnFilter = self.configuration['symbol.src.table.column.filter']
		self.symbolSrcTableColumnSelect = self.configuration['symbol.src.table.column.select']
		self.symbolDataTable = self.configuration['symbol.data.table']
		self.symbolList = self.__symbolList(symbolList)


	def perform(self, ohlcv):
		ohlcv = ohlcv.sort_values(by=['Datetime'])
		logging.debug(f'ohlcv : {ohlcv}')
		ohlcv = self.__calPctChangeWeekly(ohlcv)
  
		return ohlcv

	def __calPctChangeWeekly(self, ohlcv):
		# Calculate last 5 days moves using open and close prices
		# Formula: (current close - open from 5 days ago) / open from 5 days ago * 100
		open_5_days_ago = ohlcv['Open'].shift(5)
		ohlcv['pct_change_weekly'] = ((ohlcv['Close'] - open_5_days_ago) / open_5_days_ago * 100).round(0)
		return ohlcv


	def w_perform(self, symbol, timeframe):
		try:
			taData = DataFrame([])

			dataTableFilter = self.configuration['symbol.data.table.column.filter']
			dataTableFilter['Symbol'] = symbol
			dataTableFilter['Timeframe'] = timeframe

			database = DatabaseFactory.create(self.dbConfigPath)
			data = database.fetchRecords(tablename=self.symbolDataTable,
								tableColumnFilter=dataTableFilter)

			if len(data) == 0: raise Exception('data set empty.')
			processedData = self.perform(data)
			processedData = processedData.dropna()

			# Create new DataFrame with only required columns
			taData = DataFrame({
				'Symbol': processedData['Symbol'],
				'Datetime': processedData['Datetime'],
				'pct_change_weekly': processedData['pct_change_weekly']
			})

			logging.info(f'\n{taData}')

			# Save records to database
			database.saveRecords(self.configuration['dest.table'],
						self.configuration['dest.table.primary.keys'],
						taData)

			return 0, symbol, ''
		except Exception as e:
			traceback.print_exc()
			return -1, symbol, str(e)


	def __symbolList(self, symbolList):

		symbols = []
		if len(symbolList) == 0:
			symbols = DatabaseFactory.create(self.dbConfigPath) \
			.fetchRecords(tablename=self.symbolSrcTable,
			tableColumnFilter=self.symbolSrcTableColumnFilter, 
			tableColumnSelect=[ self.symbolSrcTableColumnSelect ],
			orderBy={}, distinct=True)[self.symbolSrcTableColumnSelect].to_list()
		else:
			symbols = symbolList
		
		symbols = list(set(symbols))
		logging.debug(symbols)
		
		return symbols


	def compute(self, timeframe):
		args = []
		for symbol in self.symbolList:
			args.append((symbol, timeframe))
   
		with Pool(50) as p:
			failedSymbols = p.starmap(self.w_perform, args)
			failedSymbols = [(symbol, reason) for status, symbol, reason in failedSymbols if status != 0]
			logging.info(f'FAILED SYMBOL : \n {failedSymbols}')

