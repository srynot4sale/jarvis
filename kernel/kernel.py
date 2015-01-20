'''
Jarvis kernel
'''
import functions.function
import application
import datetime
import pytz
import signal
import time
import tornado.ioloop
import tzlocal


class kernel(object):

    # Base functionality
    _data = {}
    _function = {}
    _interface = {}

    # Configuration dictionary
    _config = {}

    # Tornado application instance
    _application = None

    # Tornado application settings
    _appsettings = {
        'xsrf_cookies': False,
        'autoescape':   None
    }

    # Tornado application handler list
    # Attach to a URI endpoint here
    _handlers = []

    def __init__(self, config):
        self.log('Initialised')
        self.log('Load configuration')
        for c in config:
            self.setConfig(c, config[c])

    def setup(self):
        self._application = application.app(self)
        self._application.listen(self.getConfig('interface_http_port'))
        self.ioloop = tornado.ioloop.IOLoop.instance()
        self.log('Setup complete')

    def start(self):
        self.log('Initialise Tornado')

        def sig_handler(sig, frame):
            tornado.ioloop.IOLoop.instance().add_callback(shutdown)

        def shutdown():
            self.log('Shutdown initiated')
            io_loop = tornado.ioloop.IOLoop.instance()
            deadline = time.time() + 3

            def stop_loop():
                now = time.time()
                if now < deadline and (io_loop._callbacks or
                                       io_loop._timeouts):
                    io_loop.add_timeout(now + 1, stop_loop)
                else:
                    io_loop.stop()

            stop_loop()

        signal.signal(signal.SIGTERM, sig_handler)
        signal.signal(signal.SIGINT, sig_handler)

        self.log('Start IOLoop')
        self.ioloop.start()

    def log(self, message):
        server_timezone = tzlocal.get_localzone()
        now = datetime.datetime.now()
        server_time = server_timezone.localize(now).strftime('%Y-%m-%d %H:%M:%S.%f')[0:-4]
        print '%s MSG: %s' % (server_time, message)

    def debug(self, message, source=None):
        if not self.getConfig('debug'):
            return

        if source:
            print 'DEBUG %s: %s' % (source, message)
        else:
            print 'DEBUG: %s' % message

    def register(self, type, items):
        self.log('Registering %ss' % type)
        citems = getattr(self, '_'+type)

        for item in items:
            iname = item.name
            item.setKernel(self)
            citems[iname] = item
            self.log('"%s" %s registered' % (iname, type))

            # Run setup (if item has a setup method)
            if hasattr(item, 'setup'):
                item.setup()

    def get(self, type, key=None):
        citems = getattr(self, '_'+type)

        if key is None:
            return citems
        elif key in citems:
            return citems[key]
        else:
            return None

    def call(self, function, action, data=None):
        # Get function
        func = self.get('function', function)

        if func is None:
            raise JarvisException('Function does not exist', function)

        # Get action
        act = func.get_action(action)

        if act is None:
            raise JarvisException('Action does not exist', action)

        act.function = func

        # Log action (unless we're supposed to skip)
        if not act.do_not_log:

            datasource = self.get('data', 'primary')
            sql = """
                INSERT INTO
                    kernel_action_log
                    (function, action, data, timecalled)
                VALUES
                    (%s, %s, %s, NOW())
            """
            data_str = None if not data else ' '.join(unicode(x) for x in data)
            params = [function, action, data_str]
            datasource.execute(sql, params)

        # Run action
        return act().execute(data)

    def runJobs(self, type):
        # Get all functions
        funcs = self.get('function')

        for f in funcs:
            func = funcs[f]

            # Look for jobs
            job = func.get_job(type)
            if job:
                self.log('Run "%s" job for "%s"' % (type, f))
                job.function = func
                job().execute()

    def setConfig(self, key, value):
        self._config[key] = value

    def getConfig(self, key):
        if key in self._config:
            return self._config[key]
        else:
            return None

    def getDataPrimary(self):
        '''
        Get primary data interface
        '''
        return self.get('data', 'primary')

    def inClientTimezone(self, dt):
        client_timezone = pytz.timezone(self.getConfig('timezone'))
        server_timezone = tzlocal.get_localzone()
        dt = server_timezone.localize(dt)
        return dt.astimezone(client_timezone)

    def isTestMode(self):
        '''
        Return True if server running in test mode
        '''
        return bool(self.getConfig('test_mode'))


class JarvisException(Exception):
    state = functions.function.STATE_FAILURE
    httpcode = functions.function.HTTPCODE_FAILURE

    def __init__(self, message, data=[]):
        self.message = message
        self.data = data


class JarvisAuthException(JarvisException):
    state = functions.function.STATE_AUTHERR
    httpcode = functions.function.HTTPCODE_AUTHERR


class JarvisPanicException(JarvisException):
    state = functions.function.STATE_PANIC
    httpcode = functions.function.HTTPCODE_PANIC
