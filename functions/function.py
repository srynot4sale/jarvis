# Jarvis function class definition
import kernel.service
import kernel.action

STATE_SUCCESS = 1       # Response completed succesfully
STATE_FAILURE = 2       # Response failed due to user error
STATE_PANIC   = 3       # Response failed due to system error
STATE_AUTHERR = 4       # Response failed due to authentication error

HTTPCODE_SUCCESS = 200
HTTPCODE_FAILURE = 400
HTTPCODE_PANIC   = 500
HTTPCODE_AUTHERR = 401

class function(kernel.service.service):
    def __init__(self, name):
        self.name = name


    def _get_module(self):
        current = __import__('functions.%s' % self.name)
        return getattr(current, self.name)


    def get_action(self, actionname):
        func = self._get_module()
        actionattr = 'action_%s' % actionname

        if not hasattr(func, actionattr):
            try:
                return globals()[actionattr]
            except KeyError:
                return None

        return getattr(func, actionattr)


    def get_actions(self):
        func = self._get_module()

        actions = {}
        for action in dir(func):
            if action.startswith('action_'):
                actions[action] = getattr(func, action)

        return actions


    def get_job(self, type):
        func = self._get_module()

        job_type = 'job_%s' % type
        if hasattr(func, job_type):
            return getattr(func, job_type)

        return None


class response(object):

    state = None
    message = None
    data = None
    actions = None
    notification = None
    redirected = None
    write = 0

    def __init__(self, state, message = '', data = None, actions = None):
        self.state = state
        self.message = message
        self.data = data
        self.actions = actions


    def returnAdvanced(self):
        basic = {}
        basic['state'] = self.state
        basic['message'] = self.message
        basic['data'] = self.data
        basic['actions'] = self.actions
        basic['write'] = self.write
        if self.notification:
            basic['notification'] = self.notification
        if self.redirected:
            basic['redirected'] = self.redirected
        return basic


    def getHTTPCode(self):
        if self.state == STATE_SUCCESS:
            return HTTPCODE_SUCCESS

        if self.state == STATE_FAILURE:
            return HTTPCODE_FAILURE

        if self.state == STATE_PANIC:
            return HTTPCODE_PANIC

        if self.state == STATE_AUTHERR:
            return HTTPCODE_AUTHERR

        return HTTPCODE_PANIC


def redirect(action, redirect, notification = None):
    '''
    Redirect to another request, and return it's output along with a notification
    '''
    response = action.function.kernel.call(redirect[0], redirect[1], redirect[2] if len(redirect) > 2 else [])
    response.redirected = '%s %s %s' % (redirect[0], redirect[1], (' '.join(redirect[2])))
    response.notification = notification
    response.write = 1
    return response


class action_help(kernel.action.action):
    '''
    Generic "help" action for listing other actions
    in this function group
    '''

    usage = ''

    def execute(self, data):

        text = 'Usage for "%s"' % self.function.name

        usage = []
        actions = self.function.get_actions()

        keys = actions.keys()
        keys.sort()

        for action in keys:
            actionname = action[7:]

            # If action has extra usage notes, probably has parameters
            if actions[action].usage:
                ausage = ['%s %s %s' % (self.function.name, actionname, actions[action].usage)]

            # Otherwise we can link directly to the call
            else:
                call = '/%s/%s' % (self.function.name, actionname)
                ausage = ['%s %s' % (self.function.name, actionname), '%s %s' % (self.function.name, actionname)]

            usage.append(ausage)

        return response(STATE_SUCCESS, text, usage)


class action_default(action_help):
    '''
    Generic "default" action for listing common
    actions in this function group
    '''

    usage = ''
