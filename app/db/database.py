import pyodbc
from app.common.smiteapiscripts import read_config


class Database:
    def __init__(self):
        self.config = read_config()
        self.server_name = self.config[0]
        self.dbname = self.config[1]
        self.login = self.config[2]
        self.password = self.config[3]
        self.command = 'DRIVER={ODBC Driver 17 for SQL Server};' \
                      'SERVER=' + self.server_name + ';' \
                      'DATABASE=' + self.dbname + ';' \
                      'UID=' + self.login + ';' \
                      'PWD=' + self.password

    def healthcheck(self):
        try:
            connection = pyodbc.connect(self.command)
            cursor = connection.cursor()
            cursor.execute('SELECT 1')
            cursor.close()
            return 'Connection successfully'
        except Exception as Error:
            return 'Unable to reach database server. Error: ' + str(Error)

    def run_sql_query(self, query, operation):
        if operation == 'read':
            try:
                connection = pyodbc.connect(self.command)
                cursor = connection.cursor()
                cursor.execute(query)
                data = cursor.fetchall()
                return data
            except Exception as Error:
                return 'Database error:' + str(Error)
        elif operation == 'write':
            try:
                connection = pyodbc.connect(self.command)
                cursor = connection.cursor()
                cursor.execute(query)
                cursor.commit()
                return 'The operation was successful'
            except Exception as Error:
                return 'Database error:' + str(Error)