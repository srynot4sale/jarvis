# Jarvis web interface
import interface
import kernel
import kernel.kernel
import functions.function

import tornado.web
import json, os, urllib


def init(k):
    return web(k)


class web(interface.interface):

    server = None

    def __init__(self, k):
        interface.interface.__init__(self, 'web')
        self.kernel = k
        self.kernel.log('Setup HTTP interface')
        self.kernel._handlers.append((r'/', handler, dict(server=self)))
        self.kernel._handlers.append((r'/static/(.*)', statichandler, dict(server=self)))


class statichandler(tornado.web.StaticFileHandler):

    def initialize(self, server):
        self.server = server
        rootdir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        self.root = os.path.join(rootdir, 'clients', 'web', 'static')


class handler(tornado.web.RequestHandler):

    def initialize(self, server):
        self.server = server


    def get(self):

        BASEURL = self.server.kernel.getConfig('web_baseurl')
        BASEURL += 'api/'

        SECRET  = self.server.kernel.getConfig('secret')

        output = '''

<html>
<head>

<title>Jarvis</title>

<script src="/static/jquery-1.5.1.min.js"></script>
<script src="/static/global.js"></script>

<link rel="stylesheet" type="text/css" href="/static/style.css" />

</head>
<body>

<span style="display: none;" class="base_url">'''+BASEURL+'''</span>
<span style="display: none;" class="secret">'''+SECRET+'''</span>


</body>
</html>

        '''

        print 'WEB 200 /'

        if output:
            self.write(output)
