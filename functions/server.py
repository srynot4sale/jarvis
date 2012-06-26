# Jarvis list function
import function
import kernel
import kernel.action
import platform

import json, os, socket, urllib




def init():
    return serverfunc()

class serverfunc(function.function):

    def __init__(self):
        function.function.__init__(self, 'server')



class action_connect(kernel.action.action):

    def _get_weather(self):
        weather = []

        r = urllib.urlopen('http://www.metservice.com/publicData/localForecastWellington')
        data = json.loads(r.read())

        days = {'Today': 0, 'Tomorrow': 1}
        dates = days.keys()
        dates.sort()
        for day in dates:
            d = data['days'][days[day]]
            daydata = (day, d['dow'], d['date'], d['min'], d['max'], d['forecast'])
            daystr = '%s (%s %s): %s-%s&deg;C %s' % daydata
            weather.append(daystr)

        return weather

    def execute(self, func, data):
        welcome = 'Connected to Jarvis, welcome Aaron'
        data = self._get_weather()
        return function.response(function.STATE_SUCCESS, welcome, data)


class action_stats(kernel.action.action):

    def _call_ps(self, option):
        pid = os.getpid()
        return os.popen('ps -p %d -o %s | tail -1' % (pid, option)).read().strip()

    def execute(self, func, data):
        str = 'Current Jarvis server stats:'
        stats = []
        stats.append('Daemon PID: %d' % os.getpid())
        stats.append('Server address: %s:%s' % (socket.gethostname(), func.kernel.getConfig('interface_http_port')))
        stats.append('Jarvis CPU usage: %s%%' % self._call_ps('pcpu'))
        stats.append('Jarvis memory usage: %skb (%s%%)' % (self._call_ps('rss'), self._call_ps('pmem')))
        stats.append('Jarvis uptime: %s' % self._call_ps('etime'))
        stats.append('Python version: %s' % platform.release())
        stats.append('Database version: %s' % func.kernel.getConfig('version'))

        return function.response(function.STATE_SUCCESS, str, stats)
