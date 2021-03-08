from .executor import SQLExecutor


class GenericTable(SQLExecutor):
    def __init__(self):
        super(GenericTable, self).__init__()

    def __call__(self, *args, **kwargs):
        if not self.table:
            raise ValueError

    def create(self, data):
        return self._create(table=self.table,
                            data=data)

    def list(self, *args, **kwargs):
        return self._list(table=self.table,
                          fields=kwargs.pop('fields', '*'),
                          fetch_all=kwargs.pop('fetch_all', True),
                          order_by=kwargs.pop('order_by', ['-id']))

    def filter(self, *args, **kwargs):
        return self._filter(table=self.table,
                            fields=kwargs.pop('fields', '*'),
                            data=kwargs,
                            fetch_all=kwargs.pop('fetch_all', True),
                            order_by=kwargs.pop('order_by', ['-id']))

    def get(self, *args, **kwargs):
        return self._filter(table=self.table,
                            fields=kwargs.pop('fields', '*'),
                            data=kwargs,
                            fetch_all=kwargs.pop('fetch_all', False))
