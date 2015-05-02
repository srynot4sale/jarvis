# Jarvis list function
import random
import re

import function
import kernel.action


class controller(function.function):

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
    tags = None
    records = []

    def __init__(self, func, tags):

        self.func = func

        if not isinstance(tags, list):
            tags = [tags]

        self.tags = []
        for tag in tags:
            self.tags.append(normalise_tag(tag))


    def _load(self):
        """
        Load all list items that have specific tags
        """
        datasource = self.func.get_data_source()
        params = []

        sql = """
            SELECT DISTINCT
                i.*
            FROM
                function_list_items i
        """

        # Add a section for each tag
        count = 0
        for tag in self.tags:

            sql += " INNER JOIN\n"
            sql += "     function_list_tags t%d\n" % count
            sql += "  ON t%d.list_item_id = i.id\n" % count
            sql += " AND t%d.tag = %%s\n" % count
            sql += " AND t%d.deleted IS NULL\n" % count

            params.append(tag)
            count += 1

        sql += """
            WHERE
                i.deleted IS NULL
            ORDER BY
                t0.id
        """

        self.records = datasource.get_records(sql, params)

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
            data.append(normalise_tag(tag))

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

        self.add_tag(itemid, self.tags)
        return itemid

    def add_tag(self, itemid, tags):
        if not isinstance(tags, list):
            tags = [tags]

        datasource = self.func.get_data_source()

        for tag in tags:
            sql = """
                INSERT INTO
                    function_list_tags
                    (list_item_id, tag, added, deleted)
                VALUES
                    (%s, %s, NOW(), NULL)
            """
            data = [itemid, normalise_tag(tag)]
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
        data = [itemid, normalise_tag(tag)]
        datasource.execute(sql, data)
        self._load()

    def update(self, olditem, item):
        datasource = self.func.get_data_source()

        # Save old version in versions table
        sql = """
            INSERT INTO
                function_list_items_versions
                (id, item, archived)
            VALUES
                (%s, %s, NOW())
        """
        data = [olditem['id'], olditem['item']]
        datasource.execute(sql, data)

        # Update item
        sql = """
            UPDATE
                function_list_items
            SET
                item  = %s
            WHERE
                id = %s
            LIMIT
                1
        """
        data = [item, olditem['id']]
        datasource.execute(sql, data)
        self._load()

    def count(self):
        """
        Count all list items that have specific tags
        """
        self._load()
        return len(self.records)

    def get_versions(self, itemid):
        datasource = self.func.get_data_source()

        sql = """
            SELECT
                i.*
            FROM
                function_list_items_versions i
            WHERE
                i.id = %s
            ORDER BY
                i.aid DESC
        """

        params = [itemid]
        return datasource.get_records(sql, params)

    def get_old_tags(self, itemversionid):
        datasource = self.func.get_data_source()

        sql = """
            SELECT
                t.tag
            FROM
                function_list_tags t
            INNER JOIN
                function_list_items_versions i
             ON t.list_item_id = i.id
            WHERE
                i.aid = %s
            AND (
                t.deleted IS NULL
             OR t.deleted > i.archived
                )
            AND t.added < i.archived
            ORDER BY
                t.id
        """
        data = [itemversionid]
        return datasource.get_records(sql, data)


def normalise_tag(tag):
    '''
    Strip all non-alphanumeric characters and convert to lowercase
    '''
    def okchar(char):
        return char.isalnum() or char in ('!', '_')

    return filter(okchar, str(tag).lower())


def normalise_tags(tags):
    return [normalise_tag(tag) for tag in tags]


def tags_as_string(tags):
    return '"' + '", "'.join(tags) + '"'


def extract_tags(command):
    '''
    Extract tags from new list item
    '''
    tags = []
    def tag_found(match):
        tag = match.group('tag')[1:]
        tags.append(tag)
        return ''

    search = re.sub('(?<=\s)(?P<tag>\#[A-Za-z0-9\!_]+)(?=\s+|$)', tag_found, ' '+command)

    # "Unescape" escaped hashes
    search = re.sub('##', '#', search)

    return (search.strip(' '), tags)


def escape_text(text):
    return text.replace('#', '##')


class action(kernel.action.action):

    def _no_items_in_list(self, tags):
        tagstr = tags_as_string(tags)
        actions = [
            ["Add...", "list add %s %%List_item" % ' '.join(['#%s' % tag for tag in tags])],
            ["List all lists", 'list list']
        ]
        return function.response(function.STATE_SUCCESS, 'No items in list "%s"' % tagstr, [], actions)


class action_view(action):

    usage = '$listkey [$listkey ...]'

    def execute(self, tags):
        # tags in this case is a list of all the tags supplied
        # tagstr is the tags imploded around whitespace
        tags = normalise_tags(tags)
        tagstr = tags_as_string(tags)
        l = lstobj(self.function, tags)

        items = l.get_all()

        actions = []
        actions.append(["Add...", "list add #%s %%List_item" % tags[0]])
        if len(tags) > 1:
            for tag in tags:
                actions.append(["List \"%s\"" % tag, 'list view %s' % tag])

        if not len(items):
            return self._no_items_in_list(tags)

        data = []
        for item in items:
            #####
            ## Prep actions for each item
            item_actions = {'Delete':  'list remove %s %s' % (tags[0], item['id'])}

            # Only show move action if we are not showing multiple tags
            if len(tags) == 1:
                item_actions['Move...'] = 'list move %s %s %%Replacement_tag' % (item['id'], tags[0])

            item_actions['History'] = 'list history %s' % (item['id'])
            item_actions['Tag...'] = 'list tag %s %%Tag' % (item['id'])
            item_actions['Edit...'] = 'list update %s %s %%New_description{{%s}}' % (tags[0], item['id'], escape_text(item['item']))

            #####
            ## Prep tags for each item
            itemtags = l.get_tags(item['id'])
            if itemtags:
                itemtagstr = []
                for t in itemtags:
                    itemtagstr.append(t['tag'])
                    if t['tag'] in tags:
                        continue
                    item_actions['[%s]' % t['tag']] = "list view %s" % t['tag']

            #####
            ## Prep meta info
            item_meta = {'id': item['id']}

            #####
            ## Append item to the list
            data.append([item['item'], None, item_actions, item_meta])

        return function.response(function.STATE_SUCCESS, 'List %s contents' % tagstr, data, actions)


class action_list(kernel.action.action):

    def execute(self, data):
        lists = self.function.get_all_lists()
        data = []
        for ls in lists:
            # Ignore lists that begin with a hash, these are system lists
            if ls['listname'].startswith('!'):
                continue

            # Get the length of each list
            l = lstobj(self.function, ls['listname'])

            listdesc = '%s (%d)' % (ls['listname'], l.count())

            data.append([listdesc, 'list view %s' % ls['listname']])

        return function.response(function.STATE_SUCCESS, 'Lists available', data)


class action_add(kernel.action.action):

    usage = '$newitem $#tag [$#tag2 $#tag3...]'

    def execute(self, data):

        command = ' '.join(data)
        newitem, tags = extract_tags(command)

        tags = normalise_tags(tags)
        tagstr = tags_as_string(tags)

        if not len(tags):
            return function.response(function.STATE_FAILURE, 'No tag specified')

        if newitem.strip() == '':
            return function.response(function.STATE_FAILURE, 'No item to add')

        l = lstobj(self.function, tags[0])
        itemid = l.add_new(newitem)

        for tag in tags[1:]:
            l.add_tag(itemid, tag)

        return function.redirect(self, ('list', 'view', tags), 'Added "%s" with tags %s' % (newitem, tagstr))

    def undo(self, list):
        pass


class action_tag(kernel.action.action):

    usage = '$itemid $tag [$tag2 $tag3...]'

    def execute(self, data):
        itemid  = data[0]
        tags    = data[1:]

        tags = normalise_tags(tags)
        tagsstr = tags_as_string(tags)
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
            message = 'Added tags %s to "%s"' % (tagstr, itemdata['item'])
        else:
            message = 'Added tag "%s" to "%s"' % (added[0], itemdata['item'])
        return function.redirect(self, ('list', 'view', [added[0]]), message)

    def undo(self, list):
        pass


class action_move(kernel.action.action):

    usage = '$itemid $currenttag $replacementtag [$additionalnewtag1 $additionalnewtag2...]'

    def execute(self, data):
        itemid = data[0]
        oldtag = normalise_tag(data[1])
        newtags = data[2:]
        newtags = normalise_tags(newtags)
        newtagstr = tags_as_string(newtags)

        if oldtag.strip() == '':
            return function.response(function.STATE_FAILURE, 'No old tag specified')

        if len(newtags) == 0 or newtags[0].strip() == '':
            return function.response(function.STATE_FAILURE, 'No new tag specified')

        l = lstobj(self.function, oldtag)
        itemdata = l.get(itemid, oldtag)

        if not itemdata:
            return function.response(function.STATE_FAILURE, 'No item to move from tag "%s"' % oldtag)

        l.remove_tag(itemid, oldtag)

        for newtag in newtags:
            l.add_tag(itemid, newtag)

        return function.redirect(self, ('list', 'view', newtags), 'Moved "%s" from "%s" to %s' % (itemdata['item'], oldtag, newtagstr))

    def undo(self, list):
        pass


class action_delete(kernel.action.action):

    usage = '$tag $deleteid'

    def execute(self, data):
        lstkey = normalise_tag(data[0])
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
        for t in tags:
            data.append(['View list "%s"' % t['tag'], "list view %s" % t['tag']])

        resp_text = 'Deleting "%s" from "%s"' % (itemdata['item'], lstkey)

        if len(tags):
            resp = function.response(function.STATE_SUCCESS, resp_text, lstkey)
            resp.data = data
            resp.write = 1
        else:
            resp = function.redirect(self, ('list', 'view', [lstkey]), resp_text)

        return resp

    def undo(self, list):
        pass


class action_remove(action_delete):

    usage = '(alias of "list delete")'


class action_update(kernel.action.action):

    usage = '$tag $updateid $item'

    def execute(self, data):
        tag    = normalise_tag(data[0])
        itemid = data[1]
        item   = ' '.join(data[2:])

        if item.strip() == '':
            return function.response(function.STATE_FAILURE, 'No new item content')

        l = lstobj(self.function, tag)
        itemdata = l.get(itemid, tag)

        if not itemdata or item == itemdata['item']:

            if not itemdata:
                errstr = 'No item to update to "%s" in list "%s"' % (item, tag)
            else:
                errstr = 'No change made to "%s" so not updated' % (itemdata['item'])

            data = [['View list "%s"' % tag, "list view %s" % tag]]
            resp = function.response(function.STATE_FAILURE, errstr)
            resp.data = data
            resp.write = 1
            return resp

        updateditem, newtags = extract_tags(item)
        newtags = normalise_tags(newtags)

        l.update(itemdata, updateditem)

        if len(newtags):
            for newtag in newtags:
                l.add_tag(itemid, newtag)

        return function.redirect(self, ('list', 'view', [tag]), 'Updated item "%s" to "%s"' % (itemid, item))


class action_edit(action_update):

    usage = '(alias of "list update")'


class action_history(kernel.action.action):

    usage = '$itemid'

    def execute(self, data):
        itemid = data[0]
        l = lstobj(self.function, None)
        itemdata = l.get(itemid, None)

        if not itemdata:
            resp = function.response(function.STATE_FAILURE, 'No item to with id "%s"' % (itemid))
            resp.write = 1
            return resp

        items = l.get_versions(itemid)

        if not len(items):
            actions = []
            tags = l.get_tags(itemid)
            if tags:
                for t in tags:
                    actions.append(['View list "%s"' % t['tag'], "list view %s" % t['tag']])
            return function.response(function.STATE_SUCCESS, 'No previous versions of item "%s"' % (itemid), [], actions)

        data = []
        for item in items:
            item_actions = {}
            #####
            ## Prep tags for each item
            itemtags = l.get_old_tags(item['aid'])
            if itemtags:
                itemtagstr = []
                for t in itemtags:
                    itemtagstr.append(t['tag'])
                    item_actions['[%s]' % t['tag']] = "list view %s" % t['tag']

            if not len(item_actions):
                item_actions = None

            #####
            ## Append item to the list
            data.append([item['item'], None, item_actions])

        return function.response(function.STATE_SUCCESS, 'List previous versions of "%s" with id "%s"' % (itemdata['item'], itemdata['id']), data)


class action_random(action):

    usage = '$listkey [$listkey ...]'

    def execute(self, tags):
        # tags in this case is a list of all the tags supplied
        # tagstr is the tags imploded around whitespace
        tags = normalise_tags(tags)
        tagstr = tags_as_string(tags)
        l = lstobj(self.function, tags)

        items = l.get_all()
        if not len(items):
            return self._no_items_in_list(tags)

        ritem = random.choice(items)

        data = []
        data.append([ritem['item'], None])

        return function.response(function.STATE_SUCCESS, 'Random item tagged with %s' % tagstr, data)


class action_default(action_list):
    pass
