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
                t.tag AS listname
            FROM
                function_list_tags t
            WHERE
                t.deleted IS NULL
            AND t.list_item_id IN (
                SELECT
                    i.id
                FROM
                    function_list_items i
                WHERE
                    i.deleted IS NULL
            )
            ORDER BY
                t.tag
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
                i.*
            FROM
                function_list_items i
            INNER JOIN
                function_list_tags t
             ON t.list_item_id = i.id
            WHERE
                t.tag = %s
            AND t.deleted IS NULL
            AND i.deleted IS NULL
            ORDER BY
                t.id
        """
        data = [self.name]
        self.records = datasource.get_records(sql, data)

    def get_all(self):
        self._load()
        return self.records

    def add_new(self, newitem):
        datasource = self.func.get_data_source()

        # Insert item
        sql = """
            INSERT INTO
                function_list_items
                (item, added, deleted)
            VALUES
                (%s, NOW(), NULL)
        """
        data = [newitem]
        itemid = datasource.execute(sql, data).lastrowid

        # Add tag
        sql = """
            INSERT INTO
                function_list_tags
                (list_item_id, tag, added, deleted)
            VALUES
                (%s, %s, NOW(), NULL)
        """
        data = [itemid, self.name]
        datasource.execute(sql, data)
        self._load()

    def update(self, itemid, item):
        datasource = self.func.get_data_source()

        # Update item
        sql = """
            UPDATE
                function_list_items
            SET
                added = NOW(),
                item  = %s
            WHERE
                id = %s
            LIMIT
                1
        """
        data = [item, itemid]
        datasource.execute(sql, data)
        self._load()

    def delete_item(self, itemid):
        datasource = self.func.get_data_source()
        # IMPROVE SQL / protect from injection
        sql = """
            UPDATE
                function_list_items
            SET
                deleted = NOW()
            WHERE
                id = %s
            LIMIT
                1
        """
        data = [self.name, itemid]
        datasource.execute(sql, data)
        self._load()


class action_view(kernel.action.action):

    usage = '$listkey'

    def execute(self, data):
        lstkey = data[0]
        l = lstobj(self.function, lstkey)

        items = l.get_all()

        if not len(items):
            data = []
            data.append(["List all lists", 'list list'])
            return function.response(function.STATE_FAILURE, 'No items in list "%s"' % lstkey, data)

        data = []
        for item in items:
            data.append([item['item'], None, {'Delete': 'list remove %s %s' % (lstkey, item['id'])}])

        return function.response(function.STATE_SUCCESS, 'List "%s" contents' % lstkey, data)


class action_list(kernel.action.action):

    def execute(self, data):
        lists = self.function.get_all_lists()
        data = []
        for ls in lists:
            data.append([ls['listname'], 'list view %s' % ls['listname']])

        return function.response(function.STATE_SUCCESS, 'Lists available', data)


class action_add(kernel.action.action):

    usage = '$listkey $newitem'

    def execute(self, data):
        lstkey = data[0]
        newitem = ' '.join(data[1:])

        if newitem.strip() == '':
            return function.response(function.STATE_FAILURE, 'No item to add')

        l = lstobj(self.function, lstkey)
        l.add_new(newitem)

        data = []
        data.append(["View list", "list view %s" % lstkey])
        resp = function.response(function.STATE_SUCCESS, 'Adding "%s" to list "%s"' % (newitem, lstkey))
        resp.data = data
        resp.write = 1
        return resp

    def undo(self, list):
        pass


class action_delete(kernel.action.action):

    usage = '$listkey $deleteid'

    def execute(self, data):
        lstkey = data[0]
        itemid = data[1]

        l = lstobj(self.function, lstkey)
        items = l.get_all()

        itemdata = None
        for i in items:
            if i['id'] == int(itemid):
                itemdata = i
                break

        data = []
        data.append(["View list", "list view %s" % lstkey])

        if not itemdata:
            resp = function.response(function.STATE_FAILURE, 'No item to delete in list "%s"' % lstkey)
            resp.data = data
            resp.write = 1
            return resp

        l.delete_item(itemid)

        resp = function.response(function.STATE_SUCCESS, 'Deleting "%s" from "%s"' % (itemdata['item'], lstkey))
        resp.data = data
        resp.write = 1
        return resp

    def undo(self, list):
        pass


class action_remove(action_delete):

    usage = '(alias of "list delete")'


class action_update(kernel.action.action):

    usage = '$listkey $updateid $item'

    def execute(self, data):
        lstkey = data[0]
        itemid = data[1]
        item   = ' '.join(data[2:])

        if item.strip() == '':
            return function.response(function.STATE_FAILURE, 'No item to add')

        l = lstobj(self.function, lstkey)
        l.update(itemid, item)

        return function.response(function.STATE_SUCCESS, 'Updating item to "%s" to "<a href="/list/view/%s">%s</a>"' % (item, lstkey, lstkey))

    def undo(self, list):
        pass


class action_find(kernel.action.action):

    usage = '$listkey $itemtofind'

    def execute(self, data):
        lstkey = data[0]
        finditem = data[1]
        l = listobj


class action_default(action_list):
    pass
