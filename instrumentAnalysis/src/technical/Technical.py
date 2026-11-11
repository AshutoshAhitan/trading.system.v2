from pandas.core.frame import DataFrame
from ..Database.DatabaseFactory import DatabaseFactory
from multiprocessing import Pool
import logging, abc, traceback

class Technical(abc.ABC):

	def __init__(self, config, dbConfigPath, symbolList) -> None:
		super().__init__()

		self.configuration = config
		self.dbConfigPath = dbConfigPath
		self.symbolSrcTable = config['symbol.src.table']
		self.symbolSrcTableColumnFilter = config['symbol.src.table.column.filter']
		self.symbolSrcTableColumnSelect = config['symbol.src.table.column.select']
		self.symbolDataTable = config['symbol.data.table']
		self.symbolList = self.__symbolList(symbolList)


	@abc.abstractmethod
	def perform(self, data) -> DataFrame:
		pass


	def w_perform(self, symbol, timeframe):
		try:
			taData = DataFrame([])
			logging.info(f'performing ta for symbol : {symbol} and timeframe : {timeframe}')

			dataTableFilter = self.configuration['symbol.data.table.column.filter']
			dataTableFilter['Symbol'] = symbol
			dataTableFilter['Timeframe'] = timeframe

			database = DatabaseFactory.create(self.dbConfigPath)
			data = database.fetchRecords(tablename=self.symbolDataTable,
								tableColumnFilter=dataTableFilter,
								orderBy=self.configuration['symbol.data.column.orderby'],
								limit=self.configuration.get('symbol.data.limit', None))
			
			if len(data) == 0: raise Exception('data set empty.')
			if len(data) < 10: raise Exception('data set too small.')
			# Sort by 'Date' in-place
			data.sort_values(by='Datetime', inplace=True, ascending=True)

			taData = self.perform(data)
			logging.debug(taData)

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
			orderBy={})[self.symbolSrcTableColumnSelect].to_list()
		else:
			symbols = symbolList
		
		symbols = list(set(symbols))
		logging.debug(symbols)
		
		return symbols



	def compute(self, timeframe):
		args = []
		for symbol in self.symbolList:
			args.append((symbol, timeframe))
   
		with Pool(48) as p:
			failedSymbols = p.starmap(self.w_perform, args)
			failedSymbols = [(symbol, reason) for status, symbol, reason in failedSymbols if status != 0]
			logging.info(f'FAILED SYMBOL : \n {failedSymbols}')

