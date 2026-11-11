import psycopg2
import psycopg2.extras

class PostgresConnector():

    def __init__(self, configurations: dict):
        self.cursor = self.connect(configurations)


    def connect(self, configurations):
        cnxn = psycopg2.connect(
            database=configurations['database'],
            host=configurations['host'],
            port=configurations['port'],
            user=configurations['user'],
            password=configurations['password']
        )
        cnxn.autocommit = True

        return cnxn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
