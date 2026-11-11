import logging

class Database():

    def __init__(self, connector) -> None:
        self.cursor = connector.cursor

        

    def _generateWhereClause(self, columnKeyValuePairs):

        whereClause = ' WHERE '
        for aKey in columnKeyValuePairs:
            whereClause += f' "{aKey}"=\'{columnKeyValuePairs[aKey]}\' AND'

        whereClause = ' '.join(whereClause.split()[:-1])
        logging.debug(f'> where clause : {whereClause}')
        return whereClause


    def _generateSelectClause(self, columnNames):

        selectClause = ' SELECT '
        for aName in columnNames:
            selectClause += f' \"{aName}\",'

        selectClause = selectClause[:-1]
        logging.debug(f'> select clause : {selectClause}')
        return selectClause


    def _columnUpdate(self, columns, values):
        columnUpdateClause = [f'{columnName}={ColumnValue}' for columnName, ColumnValue in list(zip(columns, values))]
        columnUpdateClause = ", ".join(columnUpdateClause)
        return columnUpdateClause;


    def _getColumnNames(self, tablename):

        columns = self._getTableColumns(tablename)
        columnNames = [f'"{column_name}"' for column_name, _ in columns]

        return columnNames

    def _truncateTable(self, tablename, datetime):
        if datetime == '':
            self.cursor.execute(f"DELETE FROM \"{tablename}\"")
        else:
            self.cursor.execute(f"DELETE FROM \"{tablename}\" WHERE \"Date\" >= '{datetime}'")


