from pymssql import connect
from smiteapi.smiteapiscripts import read_db_config


class Database:
    def __init__(self):
        (server, user, passwd, dbname) = read_db_config()
        self.conn = connect(server, user, passwd, dbname, autocommit=True)
        self.cursor = self.conn.cursor()

    def healthcheck(self):
        """checks the connection to the database server"""
        try:
            self.cursor.execute("select 1")
            return 'Connection successfully'
        except Exception as Error:
            return 'Unable to reach database server. Error: ' + str(Error)

    def query(self, query, log=False):
        """send a request to the database"""
        try:
            self.cursor.execute(query)
            if log:
                print('Success')
            return True
        except Exception as err:
            if log:
                print(str(err))
            return False

    def print_cursor(self):
        for x in self.cursor:
            return x

db = Database()
