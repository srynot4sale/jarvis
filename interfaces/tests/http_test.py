import test
import functions.function


class http_testcase(test.jarvis_testcase):

    def authpositive_test(self):
        '''
        Check a positive auth works
        '''
        current_value = self.jarvis.getConfig('is_production')

        self.jarvis.setConfig('is_production', True)
        positive = self.http_request('server connect')
        assert positive['state'] == functions.function.STATE_SUCCESS

        # Reset is_production value
        self.jarvis.setConfig('is_production', current_value)


    def authnegative_test(self):
        '''
        Test that a failed auth does indeed fail
        '''
        current_value = self.jarvis.getConfig('is_production')

        self.jarvis.setConfig('is_production', True)
        negative = self.http_request('server connect', {'secret': 'badsecret'})
        assert negative['state'] == functions.function.STATE_AUTHERR
        assert negative['data'] == [['']]

        # Reset is_production value
        self.jarvis.setConfig('is_production', current_value)


    def badpath_test(self):
        '''
        Test a non existant function or action fails correctly
        '''
        yes = self.http_request('server connect')
        assert yes['state'] == functions.function.STATE_SUCCESS
        yes = None

        nofunc = self.http_request('notreal connect')
        assert nofunc['state'] == functions.function.STATE_FAILURE
        assert nofunc['message'] == 'ERROR: Function does not exist'
        nofunc = None

        noact = self.http_request('server notreal')
        assert noact['state'] == functions.function.STATE_FAILURE
        assert noact['message'] == 'ERROR: Action does not exist'
        noact = None
