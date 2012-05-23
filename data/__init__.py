import MySQLdb
import MySQLdb.cursors

import kernel
import kernel.service

def init():
    return [data()]



class data(kernel.service.service):

    name = 'primary'
    _conn = None

    def __init__(self):
        self._connect()


    def _connect(self):
        host = kernel.getConfig('data_host')
        username = kernel.getConfig('data_username')
        password = kernel.getConfig('data_password')

        # Connect to the db
        self._conn = MySQLdb.connect(
            host = host,
            db = username,
            user = username,
            passwd = password,
            cursorclass = MySQLdb.cursors.DictCursor
        )


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
