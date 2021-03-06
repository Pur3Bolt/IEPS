from .executor import SQLExecutor


class GenericTable(SQLExecutor):
    def __init__(self):
        super(GenericTable, self).__init__()

    def __call__(self, *args, **kwargs):
        if not self.table:
            raise ValueError

    def insert_into_site(self, data):
        return self._insert_into_table(self.table, data)

    def read_from_site(self, fields='*', fetch_all=True):
        return self._read_from_table(self.table, fields, fetch_all)

    def filter_site_table(self, *args, **kwargs):
        return self._filter_table(self.table, args, kwargs)
