import tornado.web

class app(tornado.web.Application):

    _kernel = None

    def __init__(self, kernel):

        self._kernel = kernel

#        settings = dict(
#            cookie_secret = "43oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=",
#            template_path = os.path.join(root_dir, "server", "templates"),
#            static_path   = os.path.join(root_dir, "server", "static"),
#            xsrf_cookies  = False,
#            autoescape    = None,
#        )
        tornado.web.Application.__init__(self, kernel._handlers, **kernel._appsettings)
