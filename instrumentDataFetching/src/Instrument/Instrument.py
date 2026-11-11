import abc
from multiprocessing import Pool
from time import sleep
from ..Database.DatabaseFactory import DatabaseFactory
import logging

class Instrument(abc.ABC):

	def __init__(self, config, dbConfigPath) -> None:
		super().__init__()
		self.configuration = config
		self.dbConfigPath = dbConfigPath

	@abc.abstractmethod
	def fetchListedInstrument(self):
		pass

	def w_fetchListedInstrument(self):
		instruments = self.fetchListedInstrument()
		DatabaseFactory.create(self.dbConfigPath).saveRecords(self.configuration['dest.table'],
														self.configuration['dest.table.primary.keys'],
														instruments)
		logging.info('Listed instruments saved.')