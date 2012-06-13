# Jarvis http interface
import cmd2 as cmd
import readline
import urllib
import requests
import json
import re


class interpreter(cmd.Cmd):

    baseurl = ''
    prompt = '> '
    secret = None


    def init(self, baseurl, secret):
        self.baseurl = baseurl
        self.secret = secret
        self._connect()
        self.cmdloop()


    def _parse_command(self, command):
        points = command.split(' ')
        params = []
        i = 0
        for point in points:
            if i <= 1:
                params.append(point)
            else:
                params[1] += ' %s' % point

            i += 1

        if len(params) > 1:
            params[1] = urllib.quote(params[1], '')

        uri = '/'.join(params)
        return uri


    def _parse_response(self, url, responseobj):
        respstr = ''
        respstr += self.colorize('%s\n' % urllib.unquote(url), 'blue')

        try:
            response = json.loads(responseobj.text)
        except ValueError:
            respstr += self.colorize('ERROR: Server\'s response could not be parsed:\n', 'red')
            respstr += responsestr
            return respstr

        color = ('green' if response['state'] == 1 else 'red')
        respstr += self.colorize(response['message'], color)
        if response['data']:
            items = response['data']
            if not isinstance(items, list):
                items = [items]

            l = 0
            for line in items:
                l+= 1
                if l == 1:
                    respstr += '\n= %s' % line
                else:
                    respstr += '\n  %s' % line

        respstr += '\n'

        # Strip HTML
        respstr = re.sub('<[^<]+?>', '', respstr)
        respstr = re.sub('&[0-9a-z]+;', '', respstr)

        return respstr


    def _handle_command(self, type, data):
        uri = self._parse_command(data)
        url = '%s/%s/%s' % (self.baseurl, type, uri)

        # Query server
        response = requests.get(url, headers={'secret': self.secret})

        print self._parse_response('%s/%s' % (type, uri), response)
        return False


    def _connect(self):
        print self.colorize('Connecting to %s' % self.baseurl, 'blue')
        return self._handle_command('server', 'connect')


    def do_quit(self, data):
        print 'Quitting! Good bye'
        return True


    def do_calendar(self, data):
        return self._handle_command('calendar', data)


    def do_list(self, data):
        return self._handle_command('list', data)


    def do_server(self, data):
        return self._handle_command('server', data)
