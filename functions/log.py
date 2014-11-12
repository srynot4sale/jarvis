# Jarvis log function
import function
import kernel.action


def init():
    return logs()


class logs(function.function):
    """
    Database calls, business logic
    """
    _datasource = None

    def __init__(self):
        function.function.__init__(self, 'log')

    def __get_data_source(self):
        if not self._datasource:
            self._datasource = self.kernel.get('data', 'primary')

        return self._datasource

    def load_latest(self):
        datasource = self.__get_data_source()
        sql = """
            SELECT
                *
            FROM
                function_log_entries
            WHERE
                deleted IS NULL
            ORDER BY
                entrytime DESC
            LIMIT 100
        """
        results = datasource.get_records(sql)
        entries = []
        for r in results:
            entries.append(log(r))

        return entries

    def get(self, entryid):
        datasource = self.__get_data_source()
        sql = """
            SELECT
                *
            FROM
                function_log_entries
            WHERE
                id = %s
            AND deleted IS NULL
        """

        result = datasource.get_record(sql, [entryid])
        if not result:
            return None
        return log(result)

    def add(self, description):
        datasource = self.__get_data_source()
        sql = """
            INSERT INTO
                function_log_entries
                (entrytime, description, deleted)
            VALUES
                (NOW(), %s, NULL)
        """
        data = [description]
        entryid = datasource.execute(sql, data).lastrowid
        return self.get(entryid)

    def remove(self, entryid):

        entry = self.get(entryid)
        if not entry:
            return None

        datasource = self.__get_data_source()
        sql = """
            UPDATE
                function_log_entries
            SET
                deleted = NOW()
            WHERE
                id = %s
        """
        datasource.execute(sql, [entryid])

        return entry


class log(object):
    id = None
    description = None
    entrytime = None

    def __init__(self, data = None):
        if data:
            self.id = data['id']
            self.description = data['description']
            self.entrytime = data['entrytime']


class action_view(kernel.action.action):

    usage = '$timeperiod'

    def execute(self, timeperiod):

        # TODO validate time period
        l = self.function.load_latest()

        actions = [("Add...", "log add %Log_entry")]

        data = []
        if not len(l):
            if len(timeperiod) and len(timeperiod[0]):
                note = "No log entries found, try a different time period"
            else:
                note = "No log entries found"

            return function.response(function.STATE_FAILURE, note, data, actions)

        for item in l:
            item_actions    = {'Delete':  'log remove %s' % (item.id)}
            item_meta       = {'id': item.id}

            item_time       = self.function.kernel.inClientTimezone(item.entrytime).strftime('%y/%m/%d %I:%M%P')
            item_text       = "%s - %s" % (item_time, item.description)

            data.append([item_text, None, item_actions, item_meta])

        if len(timeperiod) and len(timeperiod[0]):
            note = "Viewing log entries for %s" % timeperiod[0]
        else:
            note = "Viewing latest log entries"

        return function.response(function.STATE_SUCCESS, note, data, actions)


class action_add(kernel.action.action):
    """
    Add a timestamped item to the log
    """
    usage = '$description'

    def execute(self, data):
        description = ' '.join(data)

        if description.strip() == '':
            return function.response(function.STATE_FAILURE, 'No log entry specified')

        l = self.function.add(description)
        item_time = self.function.kernel.inClientTimezone(l.entrytime).strftime('%y/%m/%d %I:%M%P')

        return function.redirect(self, ('log', 'view'), 'Added log entry "%s" with timestamp "%s"' % (l.description, item_time))


class action_remove(kernel.action.action):
    """
    Remove a timestamped item to the log
    """
    usage = '$id'

    def execute(self, data):
        if not len(data):
            return function.response(function.STATE_FAILURE, 'No log entry ID specified')

        id = int(data[0])
        l = self.function.remove(id)
        if not l:
            return function.response(function.STATE_FAILURE, 'Log ID %d not found' % id)

        return function.redirect(self, ('log', 'view'), 'Deleted log entry "%s" with timestamp "%s" (ID: %d)' % (l.description, l.entrytime, l.id))


class action_delete(action_remove):
    pass


class action_default(action_view):
    pass
