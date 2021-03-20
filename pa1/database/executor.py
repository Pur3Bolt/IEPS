from .connector import Database
from .parser import prepare
from psycopg2 import extras


class SQLExecutor(Database):
    def __init__(self):
        super(SQLExecutor, self).__init__()
        self.schema = 'crawldb'

    def _create(self, table, data):
        _c = 'INSERT INTO {0}.{1} ({2}) values ({3}) RETURNING *'.format(
            self.schema,
            table,
            ','.join(data.keys()),
            ','.join(['%({})s'.format(k) for k in data.keys()]))

        if self.DEBUG:
            print("create - ", _c)

        with self.transaction() as cursor:
            query = cursor.mogrify(_c, data)
            cursor.execute(query)
            _created = cursor.fetchone()
            return _created

    def _list(self, table, fields, fetch_all=True, order_by=['-id']):
        _l = 'SELECT {0} FROM {1}.{2} ORDER BY {3}'.format(
            ','.join(fields),
            self.schema,
            table,
            ','.join(order_by))

        if self.DEBUG:
            print("list - ", _l)

        with self.transaction() as cursor:
            query = cursor.mogrify(_l)
            cursor.execute(query)

            if fetch_all:
                return cursor.fetchall()
            else:
                return cursor.fetchone()

    def _filter(self, table, fields, data, fetch_all=True, order_by=['-id']):
        _f = 'SELECT {0} FROM {1}.{2} WHERE {3} ORDER BY {4}'.format(
            ','.join(fields),
            self.schema,
            table,
            ','.join(["{0}={1}".format(k, v) for k, v in prepare(data).items()]),
            ','.join(order_by))

        if self.DEBUG:
            print("filter - ", _f)

        with self.transaction() as cursor:
            query = cursor.mogrify(_f)
            cursor.execute(query)

            if fetch_all:
                return cursor.fetchall()
            else:
                return cursor.fetchone()

    def _update(self, table, values, filters):
        _u = 'UPDATE {0}.{1} SET {2} WHERE {3} RETURNING *'.format(
            self.schema,
            table,
            ','.join(["{0}={1}".format(k, v) for k, v in prepare(values).items()]),
            ','.join(["{0}={1}".format(k, v) for k, v in prepare(filters).items()]))

        if self.DEBUG:
            print("update - ", _u)

        with self.transaction() as cursor:
            query = cursor.mogrify(_u)
            cursor.execute(query)
            _updated = cursor.fetchone()
            return _updated

    def _join(self, table_1, table_2, kind, on, filters, fields='*', fetch_all=True, order_by=None):
        _j = 'SELECT {0} FROM {1}.{2} t1 {4} JOIN {1}.{3} t2 ON {5} {6} {7}'.format(
            ','.join(fields),
            self.schema,
            table_1,
            table_2,
            kind.upper(),
            ','.join(["t1.{0}=t2.{1}".format(k, v) for k, v in on.items()]),
            'WHERE '+','.join(["{0}={1}".format(k, v) for k, v in prepare(filters).items()]) if filters else "",
            'ORDER BY '+','.join(list(map(lambda x: "-{0}.{1}".format(x.replace('-', ''), table_1)
                                          if '-' in x
                                          else "{0}.{1}".format(x, table_1), order_by))) if order_by else ""
        )

        if self.DEBUG:
            print("join - ", _j)

        # use DictCursor so we can deal with duplicated column names
        self.cursor_factory = extras.DictCursor
        with self.transaction() as cursor:
            query = cursor.mogrify(_j)
            cursor.execute(query)

            if fetch_all:
                return cursor.fetchall()
            else:
                return cursor.fetchone()