import json, logging, os.path, re, subprocess, time, urllib
import tornado.testing
from tornado.httpclient import HTTPRequest
from tornado.curl_httpclient import CurlAsyncHTTPClient

import kernel
import config


## Test suite setup and teardown functionality
log = logging.getLogger(__name__)
config.config.update(config.config_test)
config.config['test_mode'] = True


class jarvis_testcase(tornado.testing.AsyncHTTPTestCase):

    def setUp(self):
        super(jarvis_testcase, self).setUp()
        self.http_client = CurlAsyncHTTPClient(self.io_loop)
        self.headers = {'secret': config.config['secret']}

    def get_app(self):
        self.jarvis = kernel.init(config.config)
        return self.jarvis._application

    @tornado.testing.gen_test
    def http_request(self, request, headers = None):
        command = urllib.quote(request, '')
        uri = command.replace(urllib.quote(' '), '/', 2)
        url = '/api/' + uri

        if headers == None:
            headers = self.headers

        request = HTTPRequest(self.get_url(url), headers=headers)
        response = yield self.http_client.fetch(request, raise_error=False)
        raise tornado.gen.Return(json.loads(response.body))

    @tornado.testing.gen_test
    def raw_http_request(self, url, headers = None):
        if headers == None:
            headers = self.headers

        request = HTTPRequest(self.get_url(url), headers=headers)
        response = yield self.http_client.fetch(request, raise_error=False)
        raise tornado.gen.Return(response)


## Test coverage
def test_coverage():
    # Search for classes starting with action_ in the functions subdir
    matches = subprocess.check_output(["""grep -RE -o 'class action_(.*)\(.*\)' functions/ | grep -vi test"""], shell=True)
    for match in matches.split('\n'):
        if not match.strip():
            continue
        # Now pull out the function, action and a parentclass
        match = re.search('functions/([a-z0-9]+)\.py\:class action_([a-z0-9_]+)\((.*)\)', match)
        if not match:
            continue
        function = match.group(1)
        action = match.group(2)
        parentclass = match.group(3)[7:] if match.group(3)[0:7] == 'action_' else None

        # We expect this action's tests to be in the following location
        testfile = 'functions/tests/%s_test.py' % function
        if not os.path.isfile(testfile):
            count = 0
        else:
            try:
                # In the file, search for the magic string "Tests: $function_$action"
                res = """grep -RE -o '^\s*\!Tests\:\s+%s_%s$' %s""" % (function, action, testfile)
                tests = subprocess.check_output([res], shell=True)
                count = len(tests.strip().split('\n'))
            except:
                count = 0

        if parentclass:
            action += ' (%s)' % parentclass
        print('%s %s - %d tests' % (function, action, count))



if __name__ == "__main__":
    print("Run test coverage:")
    print('')
    test_coverage()
