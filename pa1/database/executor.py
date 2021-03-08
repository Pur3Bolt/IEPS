from .connector import Database


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
            ','.join(["{0}='{1}'".format(k, v) for k, v in data.items()]),
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
            ','.join(["{0}='{1}'".format(k, v) for k, v in values.items()]),
            ','.join(["{0}='{1}'".format(k, v) for k, v in filters.items()]))

        if self.DEBUG:
            print("update - ", _u)

        with self.transaction() as cursor:
            query = cursor.mogrify(_u)
            cursor.execute(query)
            _updated = cursor.fetchone()
            return _updated
