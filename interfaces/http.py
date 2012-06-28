# Jarvis http interface
import interface
import kernel
import kernel.kernel
import functions.function
#import libs.bottle as bottle

import BaseHTTPServer, json, urllib


def init(k):
    return http(k)


class http(interface.interface):

    server = None

    def __init__(self, k):
        interface.interface.__init__(self, 'http')
        self.kernel = k
        port = self.kernel.getConfig('interface_http_port')
        self.server = server(('', int(port)), handler, k)


    def start(self):
        self.kernel.log('Start serving HTTP interface')
        self.server.serve_forever()


class server(BaseHTTPServer.HTTPServer):

    kernel = None

    def __init__(self, vars, handler, k):
        self.kernel = k
        BaseHTTPServer.HTTPServer.__init__(self, vars, handler)


class handler(BaseHTTPServer.BaseHTTPRequestHandler):

    def do_GET(self):
        output = None
        httpcode = 500

        try:
            authentication = self.headers['secret'] if 'secret' in self.headers else None
            if authentication != self.server.kernel.getConfig('secret'):
                raise kernel.kernel.JarvisAuthException('Authentication failure')

            relative = self.path[1:]
            parts = relative.split('/')

            function = parts[0]
            action = parts[1] if len(parts) >= 2 else ''

            data = parts[2] if len(parts) >= 3 else ''
            data = urllib.unquote(data)
            data = data.split(' ')

            result = self.server.kernel.call(function, action, data)

            resultbasic = result.returnBasic()
            httpcode = result.getHTTPCode()
            output = json.dumps(resultbasic)

        except kernel.kernel.JarvisException as e:
            httpcode = e.httpcode
            basic = {}
            basic['state'] = e.state
            basic['message'] = 'ERROR: %s' % e.message
            basic['data'] = e.data
            output = json.dumps(basic)

        except Exception as e:
            httpcode = 500
            basic = {}
            basic['state'] = functions.function.STATE_PANIC
            basic['message'] = 'ERROR: Server panic'
            basic['data'] = []
            output = json.dumps(basic)

            # Print exception details to stdout
            import traceback, sys
            print 'EXCEPTION [%s]: %s' % (type(e).__name__, str(e))
            traceback.print_exc(file=sys.stdout)

        self.send_response(httpcode)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

        if output:
            self.wfile.write(output)
