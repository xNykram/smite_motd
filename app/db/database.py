from sqlalchemy import create_engine
from smiteapi.smiteapiscripts import read_db_config


class Database:
    def __init__(self):
        self.engine = create_engine(read_db_config())

    def healthcheck(self):
        """checks the connection to the database server"""
        try:
            with self.engine.connect() as connection:
                connection.execute("select 1")
            return 'Connection successfully'
        except Exception as Error:
            return 'Unable to reach database server. Error: ' + str(Error)

    def run_sql_query(self, query, operation):
        """send a request to the database
             :param query: request
             :param operation: direction of the request (read/write)
        """
        if operation == 'read':
            try:
                with self.engine.connect() as connection:
                    query = connection.execute(query)
                    if query is not None:
                        for row in query:
                            return row
            except Exception as Error:
                return 'Database error:' + str(Error)
        elif operation == 'write':
            try:
                with self.engine.connect() as connection:
                    connection.execute(query)
                return 'The operation was successful'
            except Exception as Error:
                return 'Database error:' + str(Error)
        else:
            return 'Expected parameter read or write'
db = Database()