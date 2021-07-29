from psycopg2 import pool, DatabaseError
import logging, os


logger = logging.getLogger()
class Database:

    __connection_pool = None

    @staticmethod
    def initialise(**kwargs):
        Database.__connection_pool = pool.SimpleConnectionPool(1, 10, **kwargs)

    @staticmethod
    def get_connection():
        return Database.__connection_pool.getconn()

    @staticmethod
    def return_connection(connection):
        Database.__connection_pool.putconn(connection)

    @staticmethod
    def close_all_connections():
        Database.__connection_pool.closeall()

class CursorFromConnectionPool:
    def __init__(self):
        self.conn = None
        self.cursor = None

    def __enter__(self):
        self.conn = Database.get_connection()
        self.cursor = self.conn.cursor()
        return self.cursor

    def __exit__(self, exception_type, exception_value, exception_traceback):
        if exception_value:  # This is equivalent to `if exception_value is not None`
            self.conn.rollback()
        else:
            self.cursor.close()
            self.conn.commit()
        Database.return_connection(self.conn)

def create_table():
    
    sql_file = open(os.path.dirname(os.path.realpath(__file__)) +'/sample.sql', 'r')

    connection_pool = None
    try:
        connection_pool = CursorFromConnectionPool()
        cursor = connection_pool.__enter__()
        cursor.execute(sql_file.read())
        connection_pool.conn.commit()
        cursor.__exit__()

    except (Exception, DatabaseError) as error:
        logger.error(error)
    finally:
        logger.info("initialized Database")
        if connection_pool is not None:
            connection_pool.conn.close()
