import pyodbc
from app.common.smiteapiscripts import read_config


class DataBase:
    def __init__(self):
        self.config = read_config()
        self.server_name = self.config[0]
        self.dbname = self.config[1]
        self.login = self.config[2]
        self.password = self.config[3]

    def test_connection(self):
        try:
            command = 'DRIVER={ODBC Driver 17 for SQL Server};' \
                      'SERVER=' + self.server_name + ';' \
                      'DATABASE=' + self.dbname + ';' \
                      'UID=' + self.login + ';' \
                      'PWD=' + self.password
            connection = pyodbc.connect(command)
            cursor = connection.cursor()
            cursor.execute('SELECT 1')
            return 'Connection successfully'
        except Exception as Error:
            return 'Unable to reach' + self.server_name + ' server, error: ' + str(Error)
