# Jarvis interface class definition
import kernel.service
import tornado.web

class interface(kernel.service.service):
    _dir = 'interfaces'

    def is_available(self):
        """Overwrite this in your child class"""
        return False


class handler(tornado.web.RequestHandler):

    def initialize(self, server):
        self.server = server

    def get_current_user(self):
        return self.get_secure_cookie('user')

    def _authenticate(self):
        # Check if this is a test site
        if not self.server.kernel.getConfig('is_production'):
            return 'admin'

        return self.get_current_user()
