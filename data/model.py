class model(object):
    """
    Generic data model

    Children must override _params = (,) with a set of strings
    representing column names
    """
    _function = None
    _datasource = None
    _kernel = None
    _params = ()

    def __init__(self, function, data = {}):
        self._function = function
        self._kernel = self._function.kernel
        self._datasource = self._function.get_data_source()
        self.set_params(data)

    def set_params(self, data):
        for i in self._params:
            clean = lambda x: x
            if hasattr(self, "_set_%s" % i):
                clean = getattr(self, "_set_%s" % i)

            if i in data:
                setattr(self, i, clean(data[i]))
            else:
                setattr(self, i, None)

    def create(self):
        sql, data = self._create_sql()
        self.id = self._datasource.execute(sql, data).lastrowid
        self.load()

    def load(self):
        sql, data = self._load_sql()
        result = self._datasource.get_record(sql, data)
        if not result:
            return False
        self.set_params(result)
        return True

    def update(self):
        sql, data = self._update_sql()
        self._datasource.execute(sql, data)
        self.load()

    def delete(self):
        sql, data = self._delete_sql()
        self._datasource.execute(sql, data)
        self.load()
