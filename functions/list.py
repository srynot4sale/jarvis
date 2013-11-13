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
            SELECT DISTINCT
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

    def get(self, itemid, tag = None):
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
                i.id = %s
            AND t.deleted IS NULL
            AND i.deleted IS NULL
        """
        if tag:
            sql += "AND t.tag = %s"
        sql += """
            ORDER BY
                t.id
        """

        data = [itemid]
        if tag:
            data.append(tag)

        return datasource.get_record(sql, data)

    def get_tags(self, itemid):
        datasource = self.func.get_data_source()

        sql = """
            SELECT
                t.tag
            FROM
                function_list_tags t
            WHERE
                t.list_item_id = %s
            AND t.deleted IS NULL
            ORDER BY
                t.id
        """
        data = [itemid]
        return datasource.get_records(sql, data)

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

        self.add_tag(itemid, self.name)

    def add_tag(self, itemid, tag):
        datasource = self.func.get_data_source()

        sql = """
            INSERT INTO
                function_list_tags
                (list_item_id, tag, added, deleted)
            VALUES
                (%s, %s, NOW(), NULL)
        """
        data = [itemid, tag]
        datasource.execute(sql, data)
        self._load()

    def remove_tag(self, itemid, tag):
        datasource = self.func.get_data_source()

        sql = """
            UPDATE
                function_list_tags
            SET
                deleted = NOW()
            WHERE
                list_item_id = %s
            AND tag = %s
        """
        data = [itemid, tag]
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


class action_view(kernel.action.action):

    usage = '$listkey'

    def execute(self, data):
        lstkey = data[0]
        l = lstobj(self.function, lstkey)

        items = l.get_all()

        actions = []
        actions.append(["Add...", "list add %s %%List_item" % lstkey])

        if not len(items):
            data = []
            data.append(["List all lists", 'list list'])
            return function.response(function.STATE_FAILURE, 'No items in list "%s"' % lstkey, data, actions)

        data = []
        for item in items:
            item_actions = {
                'Delete':  'list remove %s %s' % (lstkey, item['id']),
                'Move...': 'list move %s %s %%Replacement_tag' % (item['id'], lstkey),
                'Tag...':  'list tag %s %%Tag' % (item['id'])
            }

            tags = l.get_tags(item['id'])
            if tags:
                for t in tags:
                    if t['tag'] == lstkey:
                        continue
                    item_actions['[%s]' % t['tag']] = "list view %s" % t['tag']

            data.append([item['item'], None, item_actions])

        return function.response(function.STATE_SUCCESS, 'List "%s" contents' % lstkey, data, actions)


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

        if lstkey.strip() == '':
            return function.response(function.STATE_FAILURE, 'No tag specified')

        if newitem.strip() == '':
            return function.response(function.STATE_FAILURE, 'No item to add')

        l = lstobj(self.function, lstkey)
        l.add_new(newitem)

        return function.redirect(self, ('list', 'view', [lstkey]), 'Added "%s" to list "%s"' % (newitem, lstkey))

    def undo(self, list):
        pass


class action_tag(kernel.action.action):

    usage = '$itemid $tag [$tag2 $tag3...]'

    def execute(self, data):
        itemid  = data[0]
        tags    = data[1:]

        added = []

        for tag in tags:
            if tag.strip() == '':
                continue

            l = lstobj(self.function, tag)

            itemdata = l.get(itemid)
            data = []
            data.append(['View list "%s"' % tag, "list view %s" % tag])
            added.append(tag)

            if not itemdata:
                resp = function.response(function.STATE_FAILURE, 'No item to tag "%s"' % tag)
                resp.data = data
                resp.write = 1
                return resp

            l.add_tag(itemid, tag)

        if not added:
            return function.response(function.STATE_FAILURE, 'No tag specified')

        if len(added) > 1:
            alltags = '", "'.join(added)
            message = 'Added tags "%s" to "%s"' % (alltags, itemdata['item'])
        else:
            message = 'Added tag "%s" to "%s"' % (added[0], itemdata['item'])
        return function.redirect(self, ('list', 'view', [added[0]]), message)

    def undo(self, list):
        pass


class action_move(kernel.action.action):

    usage = '$itemid $currenttag $replacementtag'

    def execute(self, data):
        itemid = data[0]
        oldtag = data[1]
        newtag = data[2]

        if oldtag.strip() == '':
            return function.response(function.STATE_FAILURE, 'No old tag specified')

        if newtag.strip() == '':
            return function.response(function.STATE_FAILURE, 'No new tag specified')

        l = lstobj(self.function, oldtag)
        itemdata = l.get(itemid, oldtag)

        if not itemdata:
            return function.response(function.STATE_FAILURE, 'No item to move from tag "%s"' % oldtag)

        l.remove_tag(itemid, oldtag)
        l.add_tag(itemid, newtag)

        return function.redirect(self, ('list', 'view', [newtag]), 'Moved "%s" from "%s" to "%s"' % (itemdata['item'], oldtag, newtag))

    def undo(self, list):
        pass


class action_delete(kernel.action.action):

    usage = '$tag $deleteid'

    def execute(self, data):
        lstkey = data[0]
        itemid = data[1]

        l = lstobj(self.function, lstkey)
        itemdata = l.get(itemid, lstkey)

        data = []
        data.append(['View list "%s"' % lstkey, "list view %s" % lstkey])

        if not itemdata:
            resp = function.response(function.STATE_FAILURE, 'No item to delete in list "%s"' % lstkey)
            resp.data = data
            resp.write = 1
            return resp

        l.remove_tag(itemid, lstkey)

        tags = l.get_tags(itemid)
        if tags:
            for t in tags:
                data.append(['View list "%s"' % t['tag'], "list view %s" % t['tag']])

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
