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
        command = urllib.quote(command, '')
        # Replace first space with a slash (as first word is the action)
        return command.replace(urllib.quote(' '), '/', 1)


    def _parse_response(self, url, responseobj):
        respstr = ''
        respstr += self.colorize('%s\n' % urllib.unquote(url), 'blue')

        try:
            response = json.loads(responseobj.text)
        except ValueError:
            respstr += self.colorize('ERROR: Server\'s response could not be parsed:\n', 'red')
            respstr += responseobj.text
            return respstr

        color = ('green' if response['state'] == 1 else 'red')
        respstr += self.colorize(response['message'], color)
        if response['data']:
            items = response['data']

            # Make sure repsonse is a list
            if not isinstance(items, list):
                items = [items]

            # Print all the data
            for line in items:
                # If the data is a list, format it
                if isinstance(line, list):
                    respstr += '\n  %s' % '|'.join(str(l) for l in line)
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
