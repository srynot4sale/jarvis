import test
import datetime

STATE_SUCCESS = 1       # Response completed succesfully
STATE_FAILURE = 2       # Response failed due to user error
STATE_PANIC   = 3       # Response failed due to system error
STATE_AUTHERR = 4       # Response failed due to authentication error


class log_testcase(test.jarvis_testcase):

    def log_add_test(self):
        '''
        Test adding new log entries

        !Tests: log_add
        '''
        logcontent = 'Ate breakfast'

        # Check log is empty
        empty = self.http_request('log view')
        assert empty['state'] == STATE_FAILURE
        empty = None

        # Insert new item
        newitem = self.http_request('log add %s' % logcontent)
        assert newitem['state'] == STATE_SUCCESS
        message = newitem['notification']
        newitem = None

        # Parse out datetime
        dt = message.split('"')[3]

        # Build expected string
        expected = "%s - %s" % (dt, logcontent)

        # check new item exists
        exists = self.http_request('log view')
        assert exists['state'] == STATE_SUCCESS
        assert len(exists['data']) == 1
        assert exists['data'][0][0] == expected
        exists = None
