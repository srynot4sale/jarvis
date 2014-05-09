# Jarvis list function
import function
import kernel
import kernel.action
import kernel.job

import datetime, json, os, platform, pytz, re, socket, time, tzlocal, urllib




def init():
    return serverfunc()

class serverfunc(function.function):

    def __init__(self):
        function.function.__init__(self, 'server')



class job_hourly(kernel.job.job):

    def execute(self):
        weather = self.function.kernel.call('list', 'view', ['#weather'])
        dataids = []
        if weather and weather.state == function.STATE_SUCCESS:
            for d in weather.data:
                dataids.append(d[3]['id'])

        try:
            r = urllib.urlopen('http://www.metservice.com/publicData/localForecastWellington')
            data = json.loads(r.read())
        except Exception:
            return

        days = {'Today': 0, 'Tomorrow': 1}
        dates = days.keys()
        dates.sort()
        for day in dates:
            d = data['days'][days[day]]
            daydata = (day, d['min'], d['max'], d['forecast'])
            daystr = '%s: %s-%s&deg;C %s' % daydata

            if len(dataids):
                self.function.kernel.call('list', 'update', ['#weather', dataids.pop(0), daystr])
            else:
                self.function.kernel.call('list', 'add', ['#weather', daystr])


class action_connect(kernel.action.action):

    def _get_weather(self):
        return self.function.kernel.call('list', 'view', ['#weather'])

    def execute(self, data):
        user = self.function.kernel.getConfig('username')
        date = self.function.kernel.inClientTimezone(datetime.datetime.now()).strftime('%A %B %d, %Y')
        welcome = 'Hi %s. Today is %s' % (user, date)

        weather = self._get_weather()
        if weather and weather.state == function.STATE_SUCCESS:
            data = []
            for line in weather.data:
                data.append(line[0:1])
        else:
            data = []

        today = self.function.kernel.call('list', 'view', ['today'])
        if today.state == function.STATE_SUCCESS:
            data.append(['==== Today ====', 'list view today'])
            data += today.data

        actions = []
        actions.append(["Add...", "list add today %List_item"])

        return function.response(function.STATE_SUCCESS, welcome, data, actions)


class action_stats(kernel.action.action):

    def _call_ps(self, option):
        '''
        Query ps for details abou the current process
        '''
        pid = os.getpid()
        return os.popen('ps -p %d -o %s | tail -1' % (pid, option)).read().strip()

    def execute(self, data):
        str = 'Current Jarvis server stats:'

        db = self.function.kernel.getDataPrimary()
        url    = self.function.kernel.getConfig('web_baseurl')
        pid    = os.getpid()
        cpuuse = '%s%%' % self._call_ps('pcpu')
        memuse = '%skb' % self._call_ps('rss')
        uptime = self._call_ps('etime')
        pyver  = platform.release()
        dbver  = self.function.kernel.getConfig('version')

        fmt = '%Y-%m-%d %H:%M:%S %Z%z'
        server_timezone = tzlocal.get_localzone()
        now = datetime.datetime.now()
        server_time = server_timezone.localize(now)
        client_time = self.function.kernel.inClientTimezone(now)

        # Cron stuff
        crons  = db.loadConfig('lastcronstart', 0)
        cronf  = db.loadConfig('lastcronfinish', 0)
        cronl  = db.loadConfig('longestcron', 0)
        if crons != 0:
            d = datetime.datetime.fromtimestamp(float(crons))
            crons = self.function.kernel.inClientTimezone(d)

        if cronf != 0:
            d = datetime.datetime.fromtimestamp(float(cronf))
            cronf = self.function.kernel.inClientTimezone(d)

        stats = []
        stats.append('Server URL: %s' % url)
        stats.append('Daemon PID: %d' % pid)
        stats.append('Jarvis CPU usage: %s' % cpuuse)
        stats.append('Jarvis memory usage: %s' % memuse)
        stats.append('Jarvis uptime: %s' % uptime)
        stats.append('Server time: %s' % server_time.strftime(fmt))
        stats.append('Client time: %s' % client_time.strftime(fmt))
        stats.append('Last cron start: %s' % crons.strftime(fmt))
        stats.append('Last cron finish: %s' % cronf.strftime(fmt))
        stats.append('Longest cron run (secs): %s' % cronl)
        stats.append('Python version: %s' % pyver)
        stats.append('Database version: %s' % dbver)

        advdata = []
        for stat in stats:
            advdata.append([stat])

        return function.response(function.STATE_SUCCESS, str, advdata)


class action_cron(kernel.action.action):

    # Do not log calls to this action as it'll fill up the DB!
    do_not_log = True

    def execute(self, data):
        start = int(time.time())

        db = self.function.kernel.getDataPrimary()
        db.updateConfig('lastcronstart', start)

        periods = {'minute': 60, 'hourly': 3600, 'daily': 86400}
        data = []

        for period in periods:
            last = int(db.loadConfig('lastcron%s' % period, 0))
            if (last + periods[period]) <= start:
                data.append(['Running %s cron' % period])

                # Update last run time before starting in case
                # it takes longer than 60 seconds and overlaps
                # with the next cron run.
                # Unless of course the long cron run in the
                # 'minute' run, then we're screwed (and you
                # should be beaten for writing that cron job)
                db.updateConfig('lastcron%s' % period, start)
                self.function.kernel.runJobs(period)

        finish = int(time.time())
        db.updateConfig('lastcronfinish', finish)

        longest = int(db.loadConfig('longestcron', 0))
        if longest < (finish - start):
            db.updateConfig('longestcron', finish - start)

        return function.response(function.STATE_SUCCESS, 'Run cron', data)


class action_menu(kernel.action.action):

    def execute(self, data):

        message = 'Default menu items'
        items = [
            ['Home', 'server connect'],
            ['Server', 'server default'],
            ['List', 'list default'],
            ['Logs', 'log view'],
            ['Log Add', 'log add %Log_entry']
        ]

        return function.response(function.STATE_SUCCESS, message, items)
