# Jarvis habit function
import function
import kernel.action
import kernel.job

import datetime
import tzlocal


class controller(function.function):
    def date_today(self):
        return self.format_date(datetime.datetime.now())

    def date_previous(self, date):
        date = datetime.datetime.strptime(date, '%Y%m%d')
        return self.format_date(date - datetime.timedelta(1))

    def format_date(self, date):
        return self.kernel.inClientTimezone(date).strftime('%Y%m%d')

    def states(self, date):
        s = self.kernel.call('list', 'view', ['!habits_%s' % date])

        states = {}
        if s.state == function.STATE_SUCCESS:
            for item in s.data:
                parts = item[0].split('|')
                states[parts[0]] = {
                    'status':   parts[1],
                    'id':       item[3]['id']
                }

        return states

    def state(self, date, id):
        states = self.states(date)
        return states[id] if id in states.keys() else None


class action_view(kernel.action.action):

    usage = '[$date]'

    def execute(self, data):

        # TODO validate date
        if len(data) < 1 or data[0] == '':
            date = self.function.date_today()
        else:
            date = data[0]

        today = date == self.function.date_today()

        h = self.function.kernel.call('list', 'view', ['!habits'])

        actions = [
                ("Habit overview", "habit overview"),
                ("Add new habit...", "list add #!habits %Habit_name"),
                ('Previous', 'habit view %s' % self.function.date_previous(date)),
        ]

        data = []
        if h.state != function.STATE_SUCCESS:
            note = "No habits found. Add one!"
            return function.response(function.STATE_FAILURE, note, data, actions)

        complete = self.function.states(date)
        for item in h.data:
            id = str(item[3]['id'])
            # Check if complete
            c = complete[id]['status'] if id in complete.keys() else 'N'

            if c == 'N':
                item_actions = {'Completed!': 'habit update %s %s Y' % (id, date)}
                state = 'failure'
                icon = u'\u2717'
            else:
                item_actions = {'Uncomplete': 'habit update %s %s N' % (id, date)}
                state = 'success'
                icon = u'\u2713'

            item_meta       = {'id': id}
            item_text       = u'<span class="item_%s">%s</span> %s' % (state, icon, item[0])
            data.append([item_text, None, item_actions, item_meta])

        if today:
            note = 'Viewing today\'s habits'
        else:
            note = 'Viewing %s habits' % date

        return function.response(function.STATE_SUCCESS, note, data, actions)


class action_overview(kernel.action.action):

    usage = '[$date]'

    def execute(self, data):

        # TODO validate date
        if len(data) < 1 or data[0] == '':
            date = self.function.date_today()
        else:
            date = data[0]

        h = self.function.kernel.call('list', 'view', ['!habits'])

        data = []
        if h.state != function.STATE_SUCCESS:
            note = "No habits found. Add one!"
            return function.response(function.STATE_FAILURE, note, data, actions)

        dates = []
        dates.append(date)
        while len(dates) < 7:
            dates.append(self.function.date_previous(dates[-1]))

        dates.reverse()

        complete = {}
        for d in dates:
            complete[d] = self.function.states(d)

        for item in h.data:
            id = str(item[3]['id'])

            item_text = u''

            # Check if complete for each date
            for d in dates:
                comp = complete[d]
                c = comp[id]['status'] if id in comp.keys() else 'N'

                if c == 'N':
                    state = 'failure'
                    icon = u'\u2717'
                else:
                    state = 'success'
                    icon = u'\u2713'

                item_text += u'<span class="item_%s" title="%s">%s</span>' % (state, d, icon)

            item_text += ' %s' % item[0]

            data.append([item_text, None])

        note = 'Summary of habits over last 7 days'

        return function.response(function.STATE_SUCCESS, note, data)


class action_update(kernel.action.action):
    """
    Update a habit status
    """
    usage = '$habitid $date $status [$note]'

    def execute(self, data):
        habitid = data[0]
        date    = data[1]
        status  = data[2]

        current = self.function.state(date, habitid)

        if current == None:
            result = self.function.kernel.call('list', 'add', ['#!habits_%s' % date, '%s|%s' % (habitid, status)])
        else:
            result = self.function.kernel.call('list', 'update', ['!habits_%s' % date, current['id'], '%s|%s' % (habitid, status)])

        if result.state != function.STATE_SUCCESS:
            note = "Failed to update habit! (%s)" % result.message
            return function.response(function.STATE_FAILURE, note)

        if date == self.function.date_today():
            redirect = ('habit', 'view')
            date = 'today'
        else:
            redirect = ('habit', 'view', [date])

        return function.redirect(self, redirect, 'Updated habit entry for %s' % date)


class action_default(action_view):
    pass


class job_daily(kernel.job.job):
    def execute(self):
        server_timezone = tzlocal.get_localzone()
        server_time = server_timezone.localize(datetime.datetime.now() + datetime.timedelta(days=1))
        server_day = str(server_time)[0:10]

        weather = self.function.kernel.call('reminder', 'add', [server_day, '07:30:00', 'Check your habits!'])
        weather = self.function.kernel.call('reminder', 'add', [server_day, '19:30:00', 'Check your habits!'])
