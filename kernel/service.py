# Jarvis kernel service class definition


class service(object):

    name = None
    kernel = None

    def __init__(self, name):
        self.name = name

    def setKernel(self, kernel):
        self.kernel = kernel

    def _get_module(self):
        current = __import__('%s.%s' % (self._dir, self.name))
        return getattr(current, self.name)

    def get_job(self, type):
        func = self._get_module()

        job_type = 'job_%s' % type
        if hasattr(func, job_type):
            return getattr(func, job_type)

        return None
