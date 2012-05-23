# Jarvis interface class definition
import kernel.service

class interface(kernel.service.service):
    def __init__(self, name):
        self.name = name
