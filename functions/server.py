# Jarvis list function
import function
import kernel
import kernel.action
import kernel.job
import platform

import json, os, re, socket, urllib




def init():
    return serverfunc()

class serverfunc(function.function):

    def __init__(self):
        function.function.__init__(self, 'server')



class job_hourly(kernel.job.job):

    def execute(self):
        weather = self.function.kernel.call('list', 'view', ['#weather']).data
        if weather and len(weather):
            for d in weather:
                dataid = re.match('\[([0-9]+)\]', d).group(1)
                self.function.kernel.call('list', 'remove', ['#weather', dataid])

        r = urllib.urlopen('http://www.metservice.com/publicData/localForecastWellington')
        data = json.loads(r.read())

        days = {'Today': 0, 'Tomorrow': 1}
        dates = days.keys()
        dates.sort()
        for day in dates:
            d = data['days'][days[day]]
            daydata = (day, d['dow'], d['date'], d['min'], d['max'], d['forecast'])
            daystr = '%s (%s %s): %s-%s&deg;C %s' % daydata
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
        pid = os.getpid()
        return os.popen('ps -p %d -o %s | tail -1' % (pid, option)).read().strip()

    def execute(self, data):
        str = 'Current Jarvis server stats:'
        stats = []
        stats.append('Daemon PID: %d' % os.getpid())
        stats.append('Server address: %s:%s' % (socket.gethostname(), self.function.kernel.getConfig('interface_http_port')))
        stats.append('Jarvis CPU usage: %s%%' % self._call_ps('pcpu'))
        stats.append('Jarvis memory usage: %skb (%s%%)' % (self._call_ps('rss'), self._call_ps('pmem')))
        stats.append('Jarvis uptime: %s' % self._call_ps('etime'))
        stats.append('Python version: %s' % platform.release())
        stats.append('Database version: %s' % self.function.kernel.getConfig('version'))

        return function.response(function.STATE_SUCCESS, str, stats)
