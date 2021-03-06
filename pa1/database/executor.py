from .connector import Database


class SQLExecutor(Database):
    def __init__(self):
        super(SQLExecutor, self).__init__()
        self.schema = 'crawldb'

    def _insert_into_table(self, table, data):
        insert = 'INSERT INTO {0}.{1} ({2}) values ({3})'.format(
            self.schema,
            table,
            ','.join(data.keys()),
            ','.join(['%({})s'.format(k) for k in data.keys()]))

        with self.transaction() as cursor:
            query = cursor.mogrify(insert, data)
            cursor.execute(query)

    def _read_from_table(self, table, fields, fetch_all=True):
        read = 'SELECT {0} FROM {1}.{2}'.format(
            ','.join(fields),
            self.schema,
            table)

        with self.transaction() as cursor:
            query = cursor.mogrify(read)
            cursor.execute(query)

            if fetch_all:
                return cursor.fetchall()
            else:
                return cursor.fetchone()

    def _filter_table(self, table, fields, data, fetch_all=True):
        filter = 'SELECT {0} FROM {1}.{2} WHERE {3}'.format(
            ','.join(fields),
            self.schema,
            table,
            ",".join(["{0}='{1}'".format(k, v) for k, v in data.items()]))

        with self.transaction() as cursor:
            query = cursor.mogrify(filter)
            cursor.execute(query)

            if fetch_all:
                return cursor.fetchall()
            else:
                return cursor.fetchone()
