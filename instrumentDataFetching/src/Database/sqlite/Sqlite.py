from pandas import DataFrame
from ..Database import Database
import logging, pandas as pd

class Sqlite(Database):


    def __init__(self, connector) -> None:
        super().__init__(connector)
        self.__initalize__(connector)


    def __initalize__(self, connector) -> None:
        sql = """
            CREATE TABLE IF NOT EXISTS indices (
                Datetime TEXT NOT NULL,
                Timeframe TEXT NOT NULL,
                Symbol TEXT NOT NULL,
                Open REAL,
                High REAL,
                Low REAL,
                Close REAL,
                oi REAL,
                HA_Open REAL,
                HA_High REAL,
                HA_Low REAL,
                HA_Close REAL,
                Volume REAL,
                PRIMARY KEY (Timeframe, Symbol, Datetime)
            );
        """
        connector.cursor.execute(sql)

 
    def fetchRecords(self, tablename, tableColumnFilter={}, tableColumnSelect=[]):

        columnNames = self.__getColumnNames(tablename)
        columnNames = ', '.join(columnNames)
        sql = ''

        if len(tableColumnFilter) == 0 and len(tableColumnSelect) == 0:
            sql = f'SELECT {columnNames} FROM "{tablename}"'
        elif len(tableColumnFilter) != 0 and len(tableColumnSelect) == 0:
            sql = f'SELECT {columnNames} FROM "{tablename}" {self.__generateWhereClause(tableColumnFilter)}'
        elif len(tableColumnFilter) == 0 and len(tableColumnSelect) != 0:
            sql = f'{self._generateSelectClause(tableColumnSelect)} FROM "{tablename}"'
        elif len(tableColumnFilter) != 0 and len(tableColumnSelect) != 0:
            sql = f'{self._generateSelectClause(tableColumnSelect)} FROM "{tablename}" {self._generateWhereClause(tableColumnFilter)}'

        logging.debug(sql)
        self.cursor.execute(sql)

        rows = self.cursor.fetchall()
        df = pd.DataFrame(rows, columns=[desc[0] for desc in self.cursor.description])

        return df


    def saveRecords(self, tablename, primaryKeys, records: DataFrame, truncateTable=False, truncateFromDatetime=''):

        if truncateTable is True:
            logging.info('> truncating table..')
            self._truncateTable(tablename, truncateFromDatetime)

        columns = self._getTableColumns(tablename)

        sql = []
        for idx, row in records.iterrows():
            sql.append(self._generateSql(tablename, primaryKeys, columns, row))

        for aSql in sql:
            logging.debug(aSql)
            self.cursor.execute(aSql)


    def _generateSql(self, tablename, primaryKeys, columns, row):
        columns = dict(columns)
        logging.debug(f'> columns : {columns}')

        primaryKeys = [f'"{key}"' for key in primaryKeys]
        primaryKeys = ",".join(primaryKeys)

        columnNames = row.index.tolist()
        columnNames = [column_name for column_name in columnNames if column_name in columns]
        columnNamesFormatted = [f'"{column_name}"' for column_name in columnNames]
        logging.debug(f'> columnNames : {columnNames}')

        sql = f"INSERT OR REPLACE INTO \"{tablename}\" ( {', '.join(columnNamesFormatted)} ) VALUES "
        logging.debug(f'> sql : {sql}')

        values = []
        columns = dict(columns)
        for column_name in columnNames:
            val = row[column_name]
            if columns[column_name] in ['character varying', 'time without time zone', 
                                 'date', 'json', 'time with time zone', 'timestamp without time zone',
                                 'timestamp with time zone', 'TEXT']:
                if isinstance(val, str):
                    val = val.replace("'", "''")  # Escape single quotes for SQL
                values.append("'{}'".format(val))
            else:
                values.append("{}".format(val))

        logging.debug(f'> values : {values}')
        sql += f' ({", ".join(values)});'

        return sql


    def _getTableColumns(self, tablename):
        """
        Returns a list of (column_name, data_type) tuples for the given table in SQLite.
        """
        sql = f'PRAGMA table_info("{tablename}");'
        self.cursor.execute(sql)
        result = self.cursor.fetchall()
        # result is a list of tuples: (cid, name, type, notnull, dflt_value, pk)
        columns = [(row[1], row[2]) for row in result]

        logging.debug(f'> table {tablename} has columns : {columns}')

        return columns