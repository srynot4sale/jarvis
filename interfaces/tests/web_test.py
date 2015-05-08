import test
import functions.function


class web_testcase(test.jarvis_testcase):

    def auth_required_test(self):
        '''
        Check auth is required on prod but otherwise not
        '''
        current_value = self.jarvis.getConfig('is_production')

        # Prod
        self.jarvis.setConfig('is_production', True)
        prod = self.raw_http_request('')
        assert 'Login' in prod.body
        del prod

        # Non prod
        self.jarvis.setConfig('is_production', False)
        nonprod = self.raw_http_request('')
        assert 'Login' not in nonprod.body
        del nonprod

        # Reset is_production value
        self.jarvis.setConfig('is_production', current_value)
