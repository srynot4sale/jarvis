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

        # If we are in test mode, drop all tables and rerun upgrades
        if self.kernel.isTestMode():
            self.kernel.log('Dropping all tables')
            tables = self.get_records("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = %s;
            """, [self.kernel.getConfig('database_username')])

            for table in tables:
                self.execute("DROP TABLE %s" % table['table_name'])

        self._check_version()


    def _connect(self):
        host = self.kernel.getConfig('database_host')
        username = self.kernel.getConfig('database_username')
        password = self.kernel.getConfig('database_password')

        self.kernel.log('Connecting to the MySQL DB')
        # Connect to the db
        self._conn = MySQLdb.connect(
            host = host,
            db = username,
            user = username,
            passwd = password,
            cursorclass = MySQLdb.cursors.DictCursor,
            charset='utf8'
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
            self.kernel.log('Now at database version %s' % self.kernel.getConfig('version'))


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


    def get_record(self, sql, data = []):
        c = self._execute(sql, data)

        result = None
        for record in c:
            result = record
            break

        self._conn.commit()
        return result


    def execute(self, sql, data = []):
        cursor = self._execute(sql, data)
        self._conn.commit()
        return cursor


    def loadConfig(self, name, default=None):
        '''
        Attempt to load config variable from database

        Should be merged with kernel.getConfig at some point
        '''
        try:
            response = self.get_records(
                """
                SELECT
                    `value`
                FROM
                    `config`
                WHERE
                    `name` = %s
                """,
                [name]
            )
            if len(response):
                return response[0]['value']
            else:
                return default

        except Exception:
            return default


    def updateConfig(self, name, value):
        '''
        Attempt to update config variable in database

        Should be merged with kernel.setConfig at some point
        '''
        self.execute(
            """
            INSERT INTO
                `config`
            (
                `name`,
                `value`
            )
            VALUES
            (
                %s,
                %s
            )
            ON DUPLICATE KEY
            UPDATE
                `value` = VALUES(`value`)
            """,
            [
                name,
                str(value)
            ]
        )
