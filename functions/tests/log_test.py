from clients.http import make_nonprod_request as make_request
from nose.tools import with_setup
import test
import datetime

import logging

STATE_SUCCESS = 1       # Response completed succesfully
STATE_FAILURE = 2       # Response failed due to user error
STATE_PANIC   = 3       # Response failed due to system error
STATE_AUTHERR = 4       # Response failed due to authentication error

@with_setup(test.setup_function, test.teardown_function)
def log_add_test():
    '''
    Test adding new log entries

    !Tests: log_add
    '''
    logcontent = 'Ate breakfast'

    # Check log is empty
    empty = make_request('log view')
    assert empty['state'] == STATE_FAILURE
    empty = None

    # Insert new item
    newitem = make_request('log add %s' % logcontent)
    assert newitem['state'] == STATE_SUCCESS
    message = newitem['notification']
    newitem = None

    # Parse out datetime
    logging.info(message)
    dt = message.split('"')[3]

    # Build expected string
    expected = "%s - %s" % (dt, logcontent)

    # check new item exists
    exists = make_request('log view')
    assert exists['state'] == STATE_SUCCESS
    assert len(exists['data']) == 1
    assert exists['data'][0][0] == expected
    exists = None
