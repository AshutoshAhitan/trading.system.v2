from pandas import DataFrame
from ..Database import Database
import logging, pandas as pd

class Postgres(Database):

    def __init__(self, connector) -> None:
        super().__init__(connector)


    def fetchRecords(self, tablename, tableColumnFilter={}, tableColumnSelect=[], orderBy='', distinct=True, limit=None) -> DataFrame:

        columnNames = self._getColumnNames(tablename)
        columnNames = ', '.join(columnNames)
        sql = ''

        select_prefix = 'SELECT'
        if distinct:
            select_prefix = 'SELECT DISTINCT'

        if len(tableColumnFilter) == 0 and len(tableColumnSelect) == 0:
            sql = f'{select_prefix} {columnNames} FROM "{tablename}"'
        elif len(tableColumnFilter) != 0 and len(tableColumnSelect) == 0:
            sql = f'{select_prefix} {columnNames} FROM "{tablename}" {self._generateWhereClause(tableColumnFilter)}'
        elif len(tableColumnFilter) == 0 and len(tableColumnSelect) != 0:
            sql = f'{select_prefix} {self._generateSelectClause(tableColumnSelect)[7:]} FROM "{tablename}"'
        elif len(tableColumnFilter) != 0 and len(tableColumnSelect) != 0:
            sql = f'{select_prefix} {self._generateSelectClause(tableColumnSelect)[7:]} FROM "{tablename}" {self._generateWhereClause(tableColumnFilter)}'

        if len(orderBy) != 0:
            sql += f' ORDER BY {orderBy}'

        if limit is not None:
            sql += f' LIMIT {limit}'

        logging.debug(sql)
        self.cursor.execute(sql)

        rows = self.cursor.fetchall()
        rows = pd.DataFrame([i.copy() for i in rows])

        return rows



    def saveRecords(self, tablename, primaryKeys, records: DataFrame, truncateTable=False, truncateFromDatetime=''):

        if truncateTable is True:
            logging.info('> truncating table..')
            self._truncateTable(tablename, truncateFromDatetime)

        columns = self._getTableColumns(tablename)

        sql = ''
        for idx, row in records.iterrows():
            sql += self._generateSql(tablename, primaryKeys, columns, row)

        logging.debug(sql)
        self.cursor.execute(sql)



    def _generateSql(self, tablename, primaryKeys, columns, row):
        columns = dict(columns)
        logging.debug(f'> columns : {columns}')

        primaryKeys = [f'"{key}"' for key in primaryKeys]
        primaryKeys = ",".join(primaryKeys)

        columnNames = row.index.tolist()
        columnNames = [column_name for column_name in columnNames if column_name in columns]
        columnNamesFormatted = [f'"{column_name}"' for column_name in columnNames]
        logging.debug(f'> columnNames : {columnNames}')

        # columnNames = self.__getColumnNames(tablename)

        # convert list of tuples to dictinary
        # the variable is columns

        sql = f"INSERT INTO \"{tablename}\" ( {', '.join(columnNamesFormatted)} ) VALUES "
        logging.debug(f'> sql : {sql}')

        values = []
        columns = dict(columns)
        for column_name in columnNames:
            val = row[column_name]
            if columns[column_name] in ['character varying', 'time without time zone', 
                                 'date', 'json', 'time with time zone', 'timestamp without time zone',
                                 'timestamp with time zone']:
                if isinstance(val, str):
                    val = val.replace("'", "''")  # Escape single quotes for SQL
                values.append("'{}'".format(val))
            else:
                values.append("{}".format(val))

        logging.debug(f'> values : {values}')
        sql += f' ({", ".join(values)}) ON CONFLICT({primaryKeys}) DO UPDATE SET {self._columnUpdate(columnNamesFormatted, values)}; '

        return sql



    def _getTableColumns(self, tablename):

        sql = f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{tablename}';"
        # sql = "SELECT column_name, data_type FROM information_schema.columns"
        logging.debug(f'sql : {sql}')


        self.cursor.execute(sql)
        result = self.cursor.fetchall()

        columns = []
        for row in result:
            columns.append((row['column_name'], row['data_type']))

        logging.debug(f'> table {tablename} has columns : {columns}')

        return columns
