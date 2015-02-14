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
        self.kernel.log('Web interface accessible at %s' % k.getConfig('web_baseurl'))
        self.kernel._handlers.append((r'/', handler, dict(server=self)))
        self.kernel._appsettings['template_path'] = os.path.join(rootdir, 'clients', 'web')
        self.kernel._appsettings['static_path'] = os.path.join(rootdir, 'clients', 'web', 'static')


class handler(tornado.web.RequestHandler):

    def initialize(self, server):
        self.server = server


    def _authenticate(self):
        # Check if this is a test site
        if not self.server.kernel.getConfig('is_production'):
            return True

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
            self.server.kernel.log('WEB 401 /')
            self.set_status(401)
            self.set_header('WWW-Authenticate', 'Basic realm="Jarvis Web Client"')
            self.write('Please supply correct authentication details')
            return

        # Log message
        self.server.kernel.log('WEB 200 /')

        baseurl = self.server.kernel.getConfig('web_baseurl')
        secret  = self.server.kernel.getConfig('secret')

        # Add 'notprod' css class when not running in production mode
        classes = 'prod' if self.server.kernel.getConfig('is_production') else 'notprod'

        self.render("template.html", BASEURL=baseurl, SECRET=secret, BODYCLASSES=classes)
