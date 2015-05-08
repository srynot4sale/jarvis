# Jarvis http interface
import interface
import kernel
import kernel.kernel
import functions.function

import tornado.web
import json, urllib


class controller(interface.interface):

    def setup(self):
        self.kernel._handlers.append((r'/api/(.*)', handler, dict(server=self)))


class handler(interface.handler):

    def options(self, path):
        self.set_status(200)
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.set_header("Access-Control-Allow-Headers", "X-Requested-With, Content-type, Secret")
        self.set_header("Access-Control-Max-Age", "86400")

    def get(self, path):
        output = None
        httpcode = 500

        try:
            self.server.kernel.debug(path, 'interface.http.handler.get')

            # Check authentication details
            if not self._authenticate():
                authentication = self.request.headers['Secret'] if 'Secret' in self.request.headers else None
                if authentication != self.server.kernel.getConfig('secret'):
                    raise kernel.kernel.JarvisAuthException('Authentication failure')

            relative = path.lstrip('/')
            parts = relative.split('/')

            function = parts[0]
            action = parts[1] if len(parts) >= 2 else ''

            data = '/'.join(parts[2:]) if len(parts) >= 3 else ''
            data = urllib.unquote(data)
            data = data.split(' ')

            result = self.server.kernel.call(function, action, data)

            resultbasic = result.returnAdvanced()
            httpcode = result.getHTTPCode()
            output = json.dumps(resultbasic)

            self.server.kernel.debug(resultbasic['message'], 'interface.http.handler.get')

        except kernel.kernel.JarvisException as e:
            httpcode = e.httpcode
            basic = {}
            basic['state'] = e.state
            basic['message'] = 'ERROR: %s' % e.message
            basic['data'] = [[e.data]]
            output = json.dumps(basic)

            self.server.kernel.debug(basic['message'], 'interface.http.handler.get')

        except Exception as e:
            httpcode = 500
            basic = {}
            basic['state'] = functions.function.STATE_PANIC
            basic['message'] = 'ERROR: Server panic'
            basic['data'] = []
            output = json.dumps(basic)

            self.server.kernel.debug(basic['message'], 'interface.http.handler.get')

            # Print exception details to stdout
            import traceback, sys
            print 'EXCEPTION [%s]: %s' % (type(e).__name__, str(e))
            traceback.print_exc(file=sys.stdout)

        self.server.kernel.log('API %s %s' % (httpcode, path))
        self.set_status(httpcode)
        self.set_header('Content-type', 'application/json')
        self.set_header('Access-Control-Allow-Origin', '*')

        if output:
            self.write(output)
