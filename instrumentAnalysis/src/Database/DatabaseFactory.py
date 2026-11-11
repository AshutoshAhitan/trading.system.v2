from .exception import DataSinkException
from .Database import Database
from ..utils.utils import readConfigFile
from .Postgres.PostgresConnector import PostgresConnector
from .Postgres.Postgres import Postgres
from .sqlite.Sqlite import Sqlite
from .sqlite.SqliteConnector import SqliteConnector

class DatabaseFactory():

    @staticmethod
    def create(configPath: str):
        configurations = readConfigFile(configPath)

        dbtype = configurations['dbType']
        if dbtype == 'postgres':
            connector = PostgresConnector(configurations[dbtype])
            return Postgres(connector)
        elif dbtype == 'sqlite':
            connector = SqliteConnector(configurations[dbtype])
            return Sqlite(connector)
        else:
            raise DataSinkException('Data sink not valid. valid data source keyword is [postgres, sqlite]')
