# Jarvis location function
import function
import kernel.action

import datetime, json, os, platform, pytz, re, socket, time, tzlocal, urllib


class controller(function.function):
    pass


class location(object):

    def __init__(self, func):
        self.func = func

        self.id = None
        self.name = None
        self.time = None
        self.place = None
        self.reporter = None

    def add(self):
        datasource = self.func.get_data_source()

        # Insert item
        sql = """
            INSERT INTO
                function_location_logs
                (name, time, place, reporter)
            VALUES
                (%s, NOW(), %s, %s)
        """
        params = [self.name, self.place, self.reporter]
        self.id = datasource.execute(sql, params).lastrowid

    def get_latest(self, name):
        datasource = self.func.get_data_source()

        # Get latest
        sql = """
            SELECT
                *
            FROM function_location_logs
            WHERE
                name = %s
            ORDER BY time DESC
            LIMIT 1
        """
        params = [name]
        res = datasource.get_record(sql, params)

        if not res:
            return False

        for k in res:
            setattr(self, k, res[k])


class action_update(kernel.action.action):

    usage = "$name $reporter $place"

    def execute(self, data):
        name        = data[0]
        reporter    = data[1]
        place       = data[2]

        loc = location(self.function)
        loc.name = name
        loc.place = place
        loc.reporter = reporter

        loc.add()

        resp = function.response(function.STATE_SUCCESS, 'Updated "%s" location to "%s"' % (name, place))
        resp.write = 1
        return resp


class action_get(kernel.action.action):

    usage = "$name"

    def execute(self, data):
        name = data[0]

        loc = location(self.function)
        loc.get_latest(name)

        if not loc.id:
            return function.response(function.STATE_FAILURE, 'No locations reported for "%s"' % name)

        data = []
        data.append([loc.place])
        data.append([self.function.kernel.inClientTimezone(loc.time).strftime('%y/%m/%d %I:%M%P')])

        return function.response(function.STATE_SUCCESS, 'Last reported location for "%s"' % name, data)

