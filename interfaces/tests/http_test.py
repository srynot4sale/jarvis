import test

STATE_SUCCESS = 1       # Response completed succesfully
STATE_FAILURE = 2       # Response failed due to user error
STATE_PANIC   = 3       # Response failed due to system error
STATE_AUTHERR = 4       # Response failed due to authentication error


class http_testcase(test.jarvis_testcase):

    def authpositive_test(self):
        '''
        Check a positive auth works
        '''
        positive = self.http_request('server connect')
        assert positive['state'] == STATE_SUCCESS


    def authnegative_test(self):
        '''
        Test that a failed auth does indeed fail
        '''
        negative = self.http_request('server connect', {'secret': 'badsecret'})
        assert negative['state'] == STATE_AUTHERR
        assert negative['data'] == [[[]]]


    def badpath_test(self):
        '''
        Test a non existant function or action fails correctly
        '''
        yes = self.http_request('server connect')
        assert yes['state'] == STATE_SUCCESS
        yes = None

        nofunc = self.http_request('notreal connect')
        assert nofunc['state'] == STATE_FAILURE
        assert nofunc['message'] == 'ERROR: Function does not exist'
        nofunc = None

        noact = self.http_request('server notreal')
        assert noact['state'] == STATE_FAILURE
        assert noact['message'] == 'ERROR: Action does not exist'
        noact = None
