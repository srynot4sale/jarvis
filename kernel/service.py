# Jarvis kernel service class definition


class service(object):

    name = None
    kernel = None

    def __init__(self, name):
        self.name = name

    def setKernel(self, kernel):
        self.kernel = kernel
