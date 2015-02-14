# Jarvis calendar function
import function
import kernel.action

class controller(function.function):
    pass


class action_event_list(kernel.action.action):
    def execute(self, calendar):
        return []


class action_event_add(kernel.action.action):
    def execute(self, calendar):
        pass

    def undo(self, calendar):
        pass
