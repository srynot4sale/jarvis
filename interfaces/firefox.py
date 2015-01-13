# Jarvis firefox interface
import interface
import kernel
import kernel.kernel
import functions.function

import tornado.web, tornado.template
import base64, json, os, urllib


rootdir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))


def init(k):
    return firefox(k)


class firefox(interface.interface):

    server = None

    def __init__(self, k):
        interface.interface.__init__(self, 'firefox')
        self.kernel = k
        self.kernel._handlers.append((r'/firefox/(.*)', handler, dict(server=self)))


class handler(tornado.web.RequestHandler):

    def initialize(self, server):
        self.server = server

    def get(self, filename):

        baseurl = self.server.kernel.getConfig('web_baseurl')

        if filename == '':
            filename = 'index.html'

        root = os.path.join(rootdir, 'clients', 'firefox')
        loader = tornado.template.Loader(root)
        output = loader.load(filename).generate(BASEURL=baseurl)

        # Log message
        self.server.kernel.log('FIREFOX 200 %s' % filename)

        if output:
            self.write(output)
