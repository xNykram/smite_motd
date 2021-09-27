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

    def query(self, query):
        """ Send a request to the database 

            Args:
                query (str): A query to execute
        """
        self.cursor.execute(query)


db = Database()
