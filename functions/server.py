# Jarvis list function
import function
import kernel
import kernel.action
import kernel.job
import platform

import datetime, json, os, re, socket, urllib




def init():
    return serverfunc()

class serverfunc(function.function):

    def __init__(self):
        function.function.__init__(self, 'server')



class job_hourly(kernel.job.job):

    def execute(self):
        weather = self.function.kernel.call('list', 'view', ['#weather']).data
        dataids = []
        if weather and len(weather):
            for d in weather:
                dataids.append(re.match('\[([0-9]+)\]', d).group(1))

        r = urllib.urlopen('http://www.metservice.com/publicData/localForecastWellington')
        data = json.loads(r.read())

        days = {'Today': 0, 'Tomorrow': 1}
        dates = days.keys()
        dates.sort()
        for day in dates:
            d = data['days'][days[day]]
            daydata = (day, d['dow'], d['date'], d['min'], d['max'], d['forecast'])
            daystr = '%s (%s %s): %s-%s&deg;C %s' % daydata

            if len(dataids):
                self.function.kernel.call('list', 'update', ['#weather', dataids.pop(0), daystr])
            else:
                self.function.kernel.call('list', 'add', ['#weather', daystr])


class action_connect(kernel.action.action):

    def _get_weather(self):
        weather = self.function.kernel.call('list', 'view', ['#weather'])
        return weather.data

    def execute(self, data):
        welcome = 'Connected to Jarvis, welcome Aaron'
        data = self._get_weather()
        today = self.function.kernel.call('list', 'view', ['today'])
        if today.state == function.STATE_SUCCESS:
            data.append('==== Today ====')
            data += today.data

        return function.response(function.STATE_SUCCESS, welcome, data)


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
        pid    = os.getpid()
        cpuuse = '%s%%' % self._call_ps('pcpu')
        memuse = '%skb' % self._call_ps('rss')
        uptime = self._call_ps('etime')
        pyver  = platform.release()
        dbver  = self.function.kernel.getConfig('version')
        cron   = db.loadConfig('lastcron')
        if cron != 0:
            d = datetime.datetime.fromtimestamp(float(cron))
            cron = d.strftime('%Y-%m-%d %H:%M')

        stats = []
        stats.append('Daemon PID: %d' % pid)
        stats.append('Jarvis CPU usage: %s' % cpuuse)
        stats.append('Jarvis memory usage: %s' % memuse)
        stats.append('Jarvis uptime: %s' % uptime)
        stats.append('Last cron run: %s' % cron)
        stats.append('Python version: %s' % pyver)
        stats.append('Database version: %s' % dbver)

        return function.response(function.STATE_SUCCESS, str, stats)
