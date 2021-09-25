from pymssql import connect
from utils.config import read_db_config


class Database:
    """ A class responsible of connecting and making query with database """

    def __init__(self):
        (server, user, passwd, dbname) = read_db_config()
        self.conn = connect(server, user, passwd, dbname, autocommit=True)
        self.cursor = self.conn.cursor()

    def healthcheck(self) -> bool:
        """ Checks the connection to the database server 

            Returns:
                True if connection was successful
                False otherwise
        """
        try:
            self.cursor.execute("select 1")
            return True
        except Exception as Error:
            return False

    def query(self, query, log=False) -> bool:
        """ Send a request to the database 

            Args:
                query (str): A query to execute
                log (bool): A flag used for log success/error info 
                            (Default: False)

            Returns:
                True if query was executed successfully
                False otherwise
        """
        try:
            self.cursor.execute(query)
            if log:
                print('Success')
            return True
        except Exception as err:
            if log:
                print(str(err))
            return False


db = Database()
