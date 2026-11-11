import sqlite3
import os

class SqliteConnector():

    def __init__(self, configurations: dict):
        self.cursor = self.connect(configurations)


    def connect(self, configurations):
        dbfile = os.path.abspath(configurations['database'])
        cnxn = sqlite3.connect(
            dbfile,
        )
        cnxn.autocommit = True

        return cnxn.cursor()

# conn = SqliteConnector({
#     "database": "../../../../db/equities.sqlite.db"
# })

# sql = """
# Select * from indices;
# """
# conn.cursor.execute(sql)
# print(conn.cursor.fetchall())

