# Jarvis global help function
import function
import kernel.action

class controller(function.function):
    pass


class action_view(kernel.action.action):
    def execute(self, data):
        funcs = self.function.kernel.get('function').keys()
        funcs.sort()

        data = []

        for func in funcs:
            if func == 'help':
                continue

            data.append(['%s help' % func, '%s help' % func])

        return function.response(function.STATE_SUCCESS, 'Global Jarvis help menu', data)
