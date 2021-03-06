from .connector import Database


class SQLExecutor(Database):
    def __init__(self):
        super(SQLExecutor, self).__init__()
        self.schema = 'crawldb'

    def _create(self, table, data):
        _c = 'INSERT INTO {0}.{1} ({2}) values ({3})'.format(
            self.schema,
            table,
            ','.join(data.keys()),
            ','.join(['%({})s'.format(k) for k in data.keys()]))

        with self.transaction() as cursor:
            query = cursor.mogrify(_c, data)
            cursor.execute(query)

    def _list(self, table, fields, fetch_all=True):
        _l = 'SELECT {0} FROM {1}.{2}'.format(
            ','.join(fields),
            self.schema,
            table)

        with self.transaction() as cursor:
            query = cursor.mogrify(_l)
            cursor.execute(query)

            if fetch_all:
                return cursor.fetchall()
            else:
                return cursor.fetchone()

    def _filter(self, table, fields, data, fetch_all=True):
        _f = 'SELECT {0} FROM {1}.{2} WHERE {3}'.format(
            ','.join(fields),
            self.schema,
            table,
            ",".join(["{0}='{1}'".format(k, v) for k, v in data.items()]))

        with self.transaction() as cursor:
            query = cursor.mogrify(_f)
            cursor.execute(query)

            if fetch_all:
                return cursor.fetchall()
            else:
                return cursor.fetchone()
