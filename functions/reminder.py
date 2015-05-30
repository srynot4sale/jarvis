# Jarvis reminder function
import data
import data.model
import function
import kernel.action
import kernel.job

import datetime
import tzlocal

class controller(function.function):
    def list(self):
        datasource = self.get_data_source()
        sql = """
            SELECT
                *
            FROM
                function_reminder_events
            WHERE
                sent IS NULL
            ORDER BY
                `timestamp` ASC
        """
        results = datasource.get_records(sql)
        events = []
        for r in results:
            events.append(event(self, r))
        return events

    def get(self, eventid):
        datasource = self.get_data_source()
        sql = """
            SELECT
                *
            FROM
                function_reminder_events
            WHERE
                id = %s
        """

        result = datasource.get_record(sql, [eventid])
        if not result:
            return None
        return event(self, result)

    def create(self, timestamp, title):
        datasource = self.get_data_source()
        sql = """
            INSERT INTO
                function_reminder_events
                (`created`, `timestamp`, `title`)
            VALUES
                (NOW(), %s, %s)
        """
        raw = datetime.datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
        server_timestamp = self.kernel.inServerTimezone(raw).strftime('%Y-%m-%d %H:%M:%S')

        data = [server_timestamp, title]
        entryid = datasource.execute(sql, data).lastrowid
        return self.get(entryid)

    def update(self, eventobj, params):
        datasource = self.get_data_source()

        param_sql_cols = []
        for p in params.keys():
            param_sql_cols.append('`%s` = %%s' % p)

        sql = """
            UPDATE
                function_reminder_events
            SET
                %s
            WHERE
                id = %%s
        """ % (','.join(param_sql_cols))

        data = params.values() + [eventobj.id]
        datasource.execute(sql, data)
        return eventobj.set_params(params)


class event(data.model.model):
    _params = ('id', 'created', 'timestamp', 'title', 'sent', 'method')

    def get_nice_time(self):
        return self._kernel.inClientTimezone(self.timestamp).strftime('%y/%m/%d %I:%M%P')

    def update(self, params):
        return self._function.update(self, params)


class action_add(kernel.action.action):
    """
    Add a reminder
    """
    usage = '$timestamp $title'

    def execute(self, data):
        timestamp = ' '.join(data[0:2])
        title = ' '.join(data[2:])

        if title.strip() == '':
            return function.response(function.STATE_FAILURE, 'No title supplied')

        e = self.function.create(timestamp, title)

        return function.redirect(
            self,
            ('reminder', 'list'),
            notification='Added reminder event "%s" with timestamp "%s"' % (e.title, e.get_nice_time())
        )


class action_list(kernel.action.action):
    """
    List upcoming reminders
    """

    def execute(self, data):
        events = self.function.list()
        data = []
        for e in events:
            data.append(['%s - %s' % (e.get_nice_time(), e.title)])

        actions = [('Add new...', 'reminder add %Timestamp %Title')]

        return function.response(function.STATE_SUCCESS, 'Upcoming reminders', data, actions)


class job_minute(kernel.job.job):

    def execute(self):
        server_timezone = tzlocal.get_localzone()
        server_time = server_timezone.localize(datetime.datetime.now())

        events = self.function.list()
        for e in events:
            timestamp = server_timezone.localize(e.timestamp)
            if timestamp <= server_time:

                # Send email
                self.function.kernel.get('interface', 'email').send_to_self(
                    'Reminder - %s' % e.title,
                    '%s\n\nSent by Jarvis' % (e.get_nice_time())
                )

                # Mark as sent
                e.update({
                    'sent': data.make_db_timestamp(server_time),
                    'method': 'email'
                })
