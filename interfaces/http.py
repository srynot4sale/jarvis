# Jarvis http interface
import interface
import kernel
#import libs.bottle as bottle

import BaseHTTPServer, json, urllib


def init(k):
    return http(k)


class http(interface.interface):

    server = None

    def __init__(self, k):
        interface.interface.__init__(self, 'http')
        self.kernel = k
        port = kernel.getConfig('interface_http_port')
        self.server = server(('', int(port)), handler, k)
        self.server.serve_forever()


class server(BaseHTTPServer.HTTPServer):

    kernel = None

    def __init__(self, vars, handler, k):
        self.kernel = k
        BaseHTTPServer.HTTPServer.__init__(self, vars, handler)


class handler(BaseHTTPServer.BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

        relative = self.path[1:]
        parts = relative.split('/')

        function = parts[0]
        action = parts[1] if len(parts) >= 2 else ''

        data = parts[2] if len(parts) >= 3 else ''
        data = urllib.unquote(data)
        data = data.split(' ')

        result = self.server.kernel.call(function, action, data)

        resultbasic = result.returnBasic()

        self.wfile.write(json.dumps(resultbasic))
