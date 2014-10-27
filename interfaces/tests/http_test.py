from clients.http import make_nonprod_request as make_request
from nose.tools import with_setup
import test

@with_setup(test.setup_function, test.teardown_function)
def authpositive_test():
    '''
    Check a positive auth works
    '''
    positive = make_request('server connect')
    assert positive['state'] == 1

@with_setup(test.setup_function, test.teardown_function)
def authnegative_test():
    '''
    Test that a failed auth does indeed fail
    '''
    negative = make_request('server connect', 'badsecret')
    assert negative['state'] == 4
    assert negative['data'] == [[[]]]

@with_setup(test.setup_function, test.teardown_function)
def badpath_test():
    '''
    Test a non existant function or action fails correctly
    '''
    yes = make_request('server connect')
    assert yes['state'] == 1
    yes = None

    nofunc = make_request('notreal connect')
    assert nofunc['state'] == 2
    assert nofunc['message'] == 'ERROR: Function does not exist'
    nofunc = None

    noact = make_request('server notreal')
    assert noact['state'] == 2
    assert noact['message'] == 'ERROR: Action does not exist'
    noact = None
