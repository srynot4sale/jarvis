import tornado.web


class app(tornado.web.Application):

    _kernel = None

    def __init__(self, kernel):
        self._kernel = kernel
        tornado.web.Application.__init__(self, kernel._handlers,
                                         **kernel._appsettings)
