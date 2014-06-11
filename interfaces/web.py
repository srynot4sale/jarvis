# Jarvis web interface
import interface
import kernel
import kernel.kernel
import functions.function

import tornado.web, tornado.template
import base64, json, os, urllib


rootdir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))


def init(k):
    return web(k)


class web(interface.interface):

    server = None

    def __init__(self, k):
        interface.interface.__init__(self, 'web')
        self.kernel = k
        self.kernel.log('Setup web interface')
        self.kernel.log('Interface accessible at %s' % k.getConfig('web_baseurl'))
        self.kernel._handlers.append((r'/', handler, dict(server=self)))
        self.kernel._handlers.append((r'/static/(.*)', statichandler, dict(server=self)))


class statichandler(tornado.web.StaticFileHandler):

    def initialize(self, server):
        self.server = server
        self.root = os.path.join(rootdir, 'clients', 'web', 'static')


class handler(tornado.web.RequestHandler):

    def initialize(self, server):
        self.server = server


    def _authenticate(self):
        # Check authorised header exists
        if 'Authorization' not in self.request.headers:
            return False

        auth = self.request.headers['Authorization']

        # Check it is well formed
        if not auth.startswith('Basic '):
            return False

        # Remove 'Basic ' prefix
        auth = auth[6:]

        username = self.server.kernel.getConfig('web_username')
        password = self.server.kernel.getConfig('web_password')

        return base64.b64decode(auth) == ('%s:%s' % (username, password))


    def get(self):

        # Check authentication details
        if not self._authenticate():
            self.set_status(401)
            self.set_header('WWW-Authenticate', 'Basic realm="Jarvis Web Client"')
            self.write('Please supply correct authentication details')
            return

        baseurl = self.server.kernel.getConfig('web_baseurl')
        secret  = self.server.kernel.getConfig('secret')

        root = os.path.join(rootdir, 'clients', 'web')
        loader = tornado.template.Loader(root)
        output = loader.load("template.html").generate(BASEURL=baseurl, SECRET=secret)

        # Log message
        self.server.kernel.log('WEB 200 /')

        if output:
            self.write(output)
