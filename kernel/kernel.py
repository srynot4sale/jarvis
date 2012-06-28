## Jarvis kernel
import functions.function

class kernel(object):

    _data = {}
    _function = {}
    _interface = {}
    _config = {}


    def __init__(self, config):
        self.log('Initialised')
        self.log('Load configuration')
        for c in config:
            self.setConfig(c, config[c])


    def log(self, message):
        print 'MSG: %s' % message


    def register(self, type, items):
        self.log('Registering %ss' % type)
        citems = getattr(self, '_'+type)

        for item in items:
            iname = item.name
            item.setKernel(self)
            citems[iname] = item
            self.log('"%s" %s registered' % (iname, type))


    def get(self, type, key = None):
        citems = getattr(self, '_'+type)

        if key == None:
            return citems
        elif key in citems:
            return citems[key]
        else:
            return None


    def call(self, function, action, data = None):
        # Get function
        func = self.get('function', function)

        if func == None:
            raise JarvisException('Function does not exist', function)

        # Get action
        act = func.get_action(action)

        if act == None:
            raise JarvisException('Action does not exist', action)

        # Run action
        act.function = func
        return act().execute(func, data)


    def setConfig(self, key, value):
        self._config[key] = value


    def getConfig(self, key):
        return self._config[key]


class JarvisException(Exception):
    state = functions.function.STATE_FAILURE
    httpcode = functions.function.HTTPCODE_FAILURE

    def __init__(self, message, data = []):
        self.message = message
        self.data = data

class JarvisAuthException(JarvisException):
    state = functions.function.STATE_AUTHERR
    httpcode = functions.function.HTTPCODE_AUTHERR

class JarvisPanicException(JarvisException):
    state = functions.function.STATE_PANIC
    httpcode = functions.function.HTTPCODE_PANIC
