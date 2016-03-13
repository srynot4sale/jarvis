# Jarvis web interface
import interface
import kernel
import kernel.kernel
import functions.function

import tornado.web, tornado.template
import base64, json, os, urllib


rootdir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))


class controller(interface.interface):
    def setup(self):
        # Check if menu system list empty, and if so fill with default data
        menu = self.kernel.call('list', 'view', ['#!menu'])
        if not len(menu.data):
            self.kernel.log('Setup default menu for web interface')
            self.kernel.call('list', 'add', ['#!menu', 'Home | server connect'])
            self.kernel.call('list', 'add', ['#!menu', 'List | list default'])
            self.kernel.call('list', 'add', ['#!menu', 'Help | help default'])

        self.kernel.log('Web interface accessible at %s' % self.kernel.getConfig('web_baseurl'))
        self.kernel._handlers.append((r'/', handler, dict(server=self)))
        self.kernel._handlers.append((r'/logout', handler, dict(server=self)))
        self.kernel._appsettings['template_path'] = os.path.join(rootdir, 'clients', 'web')
        self.kernel._appsettings['static_path'] = os.path.join(rootdir, 'clients', 'web', 'static')
        self.kernel._appsettings['login_url'] = '/'
        self.kernel._appsettings['cookie_secret'] = self.kernel.getConfig('secret')


class handler(interface.handler):

    def post(self):
        self.server.kernel.log('WEB AUTH /')

        post_username = self.get_argument('username', '')
        post_password = self.get_argument('password', '')
        username = self.server.kernel.getConfig('web_username')
        password = self.server.kernel.getConfig('web_password')

        if username == post_username and password == post_password:
            self.server.kernel.log('Logged in as "%s"' % username)
            self.set_current_user(username)
            self.redirect(self.get_argument("next", u"/"))
        else:
            self.server.kernel.log('Login failure for user "%s"' % username)
            self.set_current_user(None)

            # Send email
            self.server.kernel.get('interface', 'email').send_to_self(
                'Web Authentication failure',
                'Sent by Jarvis'
            )

            self.redirect('/')

    def set_current_user(self, user):
        if user:
            self.set_secure_cookie("user", tornado.escape.json_encode(user))
        else:
            self.clear_cookie("user")

    def get(self):
        # Check authentication details
        if not self._authenticate():
            # Show login page
            self.server.kernel.log('WEB 401 /')
            self.render("template-login.html")
            return

        # Check if logging out
        if self.request.uri == '/logout':
            self.server.kernel.log('WEB LOGOUT /')
            self.set_current_user(None)
            self.redirect('/')
            return

        # Log message
        self.server.kernel.log('WEB 200 /')

        baseurl = self.server.kernel.getConfig('web_baseurl')

        # Add 'notprod' css class when not running in production mode
        classes = 'prod' if self.server.kernel.getConfig('is_production') else 'notprod'

        self.render("template.html", BASEURL=baseurl, BODYCLASSES=classes)
