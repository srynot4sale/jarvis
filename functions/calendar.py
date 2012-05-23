# Jarvis calendar function
import function
import kernel.action

def init():
    return calendar()

class calendar(function.function):

    _datasource = None

    def __init__(self):
        function.function.__init__(self, 'calendar')


    def get_data_source(self):
        if not self._datasource:
            self._datasource = self.kernel.get('data', 'primary')

        return self._datasource


class action_event_list(kernel.action.action):
    def execute(self, calendar):
        return []


class action_event_add(kernel.action.action):
    def execute(self, calendar):
        pass

    def undo(self, calendar):
        pass
