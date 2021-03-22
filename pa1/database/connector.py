from contextlib import contextmanager
from psycopg2 import connect, extras
from threading import Lock


class Database:
    def __init__(self, autoconnect=True):
        super(Database, self).__init__()

        self.DEBUG = False
        self.lock = Lock()

        self.username = 'user'
        self.password = 'SecretPassword'
        self.host = 'localhost'
        self.port = '5432'
        self.dbname = ''

        self.DSN = "dbname='%s' user='%s' host='%s' password='%s'" \
                   % (self.dbname, self.username, self.host, self.password)

        self.cursor_factory = extras.RealDictCursor
        self.connection, self.cursor = None, None

        if autoconnect:
            self.connection = self.get_connection()

    def test(self):
        with self.transaction() as cur:
            cur.execute("SELECT 1;")
            return True

    def set_debug(self, value=True):
        self.DEBUG = value

    def get_connection(self):
        if self.connection and not self.connection.closed:
            return self.connection
        else:
            conn = connect(self.DSN)
            self.connection = conn
            return self.connection

    def get_cursor(self, conn=None):
        if not conn:
            conn = self.get_connection()
        if conn.closed:
            conn = self.get_connection()
        if self.cursor and not self.cursor.closed:
            return self.cursor
        self.cursor = conn.cursor(cursor_factory=self.cursor_factory)
        return self.cursor

    @contextmanager
    def transaction(self):
        con, cur = None, None
        with self.lock:
            try:
                con = self.get_connection()
                cur = self.get_cursor(con)
                yield cur
                con.commit()
            except Exception as e:
                if con:
                    con.rollback()
                raise e
            finally:
                if cur:
                    cur.close()
                if False and con:
                    con.close()
