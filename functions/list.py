# Jarvis list function
import function
import kernel.action

def init():
    return lstfunc()

class lstfunc(function.function):

    _datasource = None

    def __init__(self):
        function.function.__init__(self, 'list')

    def get_data_source(self):
        if not self._datasource:
            self._datasource = self.kernel.get('data', 'primary')

        return self._datasource

    def get_all_lists(self):
        datasource = self.get_data_source()
        sql = """
            SELECT DISTINCT
                listname
            FROM
                function_list_items
            ORDER BY
                listname
        """
        return datasource.get_records(sql)


class lstobj(object):

    func = None
    name = None
    records = []

    def __init__(self, func, name):
        self.func = func
        self.name = name

    def _load(self):
        datasource = self.func.get_data_source()
        sql = """
            SELECT
                *
            FROM
                function_list_items
            WHERE
                listname = %s
            ORDER BY
                id
        """
        data = [self.name]
        self.records = datasource.get_records(sql, data)

    def get_all(self):
        self._load()
        return self.records

    def add_new(self, newitem):
        datasource = self.func.get_data_source()
        # IMPROVE SQL / protect from injection
        sql = """
            INSERT INTO
                function_list_items
                (listname, item)
            VALUES
                (%s, %s)
        """
        data = [self.name, newitem]
        datasource.execute(sql, data)
        self._load()

    def delete_item(self, itemid):
        datasource = self.func.get_data_source()
        # IMPROVE SQL / protect from injection
        sql = """
            DELETE FROM
                function_list_items
            WHERE
                listname = %s
            AND id = %s
            LIMIT
                1
        """
        data = [self.name, itemid]
        datasource.execute(sql, data)
        self._load()


class action_view(kernel.action.action):

    usage = '$listkey'

    def execute(self, func, data):
        lstkey = data[0]
        l = lstobj(func, lstkey)

        items = l.get_all()

        if not len(items):
            return function.response(function.STATE_FAILURE, 'No items in list "%s" (<a href="/list/list">List all</a>)' % lstkey)

        data = []
        for item in items:
            data.append('[%s] %s' % (item['id'], item['item']))

        return function.response(function.STATE_SUCCESS, 'List "%s" contents' % lstkey, data)


class action_list(kernel.action.action):

    def execute(self, func, data):
        lists = func.get_all_lists()
        data = []
        for ls in lists:
            data.append('<a href="/list/view/%s">%s</a>' % (ls['listname'], ls['listname']))

        return function.response(function.STATE_SUCCESS, 'Lists available', data)


class action_add(kernel.action.action):

    usage = '$listkey $newitem'

    def execute(self, func, data):
        lstkey = data[0]
        newitem = ' '.join(data[1:])

        if newitem.strip() == '':
            return function.response(function.STATE_FAILURE, 'No item to add')

        l = lstobj(func, lstkey)
        l.add_new(newitem)

        return function.response(function.STATE_SUCCESS, 'Adding "%s" to "<a href="/list/view/%s">%s</a>"' % (newitem, lstkey, lstkey))

    def undo(self, list):
        pass


class action_delete(kernel.action.action):

    usage = '$listkey $deleteid'

    def execute(self, func, data):
        lstkey = data[0]
        itemid = data[1]

        l = lstobj(func, lstkey)
        items = l.get_all()

        itemdata = None
        data = []
        for i in items:
            data.append('%s %s' % (i['id'], itemid))
            if i['id'] == int(itemid):
                itemdata = i
                break

        if not itemdata:
            return function.response(function.STATE_FAILURE, 'No item to delete in "<a href="/list/view/%s">%s</a>"' % (lstkey, lstkey), data)

        l.delete_item(itemid)

        return function.response(function.STATE_SUCCESS, 'Deleting "%s" from "<a href="/list/view/%s">%s</a>"' % (itemdata['item'], lstkey, lstkey))

    def undo(self, list):
        pass


class action_remove(action_delete):

    usage = '(alias of "list delete")'


class action_find(kernel.action.action):

    usage = '$listkey $itemtofind'

    def execute(self, func, data):
        lstkey = data[0]
        finditem = data[1]
        l = listobj
