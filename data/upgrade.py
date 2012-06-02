import data
import kernel

database_version = 1

def check(data):
    '''
    Check version of database structure
    '''
    current = get_version(data)
    kernel.setConfig('version', current)
    return current >= database_version


def get_version(data):
    '''
    Attempt to find version of database structure
    '''
    try:
        version = data.get_records(
            """
            SELECT
                `value`
            FROM
                `config`
            WHERE
                `name` = %s
            """,
            ['version']
        )
        if len(version):
            return int(version[0]['value'])
        else:
            return 0

    except Exception:
        return 0


def set_version(data, version):
    '''
    Set version in database
    '''
    data.execute(
        """
        UPDATE
            `config`
        SET
            `value` = %s
        WHERE
            `name` = %s
        """,
        [
            version,
            'version'
        ]
    )


def run(data):
    current = get_version(data)

    version = 1
    if current < version:
        data.execute(
            """
            CREATE TABLE IF NOT EXISTS `config` (
              `uid` int(10) unsigned NOT NULL AUTO_INCREMENT,
              `name` varchar(255) NOT NULL,
              `value` text NOT NULL,
              PRIMARY KEY (`uid`),
              UNIQUE KEY `name` (`name`)
            ) ENGINE=MyISAM DEFAULT CHARSET=utf8;
            """
        )

        data.execute(
            """
            INSERT INTO
                `config`
                (`name`, `value`)
            VALUES
                (%s, %s)
            """,
            [
                'version',
                '0'
            ]
        )
        set_version(data, version)

    kernel.setConfig('version', current)
