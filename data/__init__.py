import MySQLdb
import MySQLdb.cursors

import kernel.service

def init(jarvis):
    return [data(jarvis)]



class data(kernel.service.service):

    name = 'primary'
    _conn = None

    def __init__(self, jarvis):
        '''
        Initialise database connection and check structure
        '''
        self.kernel = jarvis
        self._connect()
        self._check_version()


    def _connect(self):
        host = self.kernel.getConfig('data_host')
        username = self.kernel.getConfig('data_username')
        password = self.kernel.getConfig('data_password')

        # Connect to the db
        self._conn = MySQLdb.connect(
            host = host,
            db = username,
            user = username,
            passwd = password,
            cursorclass = MySQLdb.cursors.DictCursor
        )


    def _check_version(self):
        '''
        Check to see if the database structure is up-to-date,
        and if not - upgrade it
        '''
        import data.upgrade
        if not data.upgrade.check(self):
            self.kernel.log('Running database upgrade')
            data.upgrade.run(self)



    def _execute(self, sql, data = [], noretry = False):
        try:
            # Attempt query
            c = self._conn.cursor()
            c.execute(sql, data)
        except (AttributeError, MySQLdb.OperationalError):
            # If failed for a second time
            if noretry:
                return None

            # If first failure, recurse!
            self._connect()
            return self._execute(sql, data, True)

        return c


    def get_records(self, sql, data = []):
        c = self._execute(sql, data)

        result = []
        for record in c:
            result.append(record)

        self._conn.commit()
        return result


    def execute(self, sql, data = []):
        self._execute(sql, data)
        self._conn.commit()
