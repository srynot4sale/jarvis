import data
import kernel

database_version = 3

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

    kernel.setConfig('version', version)

    version = 2
    if current < version:
        data.execute(
            """
            CREATE TABLE IF NOT EXISTS `function_calendar_events` (
              `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
              `datetime` datetime NOT NULL,
              PRIMARY KEY (`id`),
              KEY `datetime` (`datetime`)
            ) ENGINE=MyISAM DEFAULT CHARSET=latin1 ;
            """
        )

        data.execute(
            """
            CREATE TABLE IF NOT EXISTS `function_list_items` (
              `listname` varchar(255) CHARACTER SET utf8 NOT NULL,
              `item` varchar(255) CHARACTER SET utf8 NOT NULL,
              `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
              PRIMARY KEY (`id`),
              KEY `item` (`item`),
              KEY `listname` (`listname`)
            ) ENGINE=MyISAM  DEFAULT CHARSET=latin1 ;
            """
        )

        set_version(data, version)

    kernel.setConfig('version', version)

    version = 3
    if current < version:
        data.execute(
            """
            ALTER TABLE  `function_list_items` ADD  `added` DATETIME NULL ,
            ADD  `deleted` DATETIME NULL ,
            ADD INDEX (  `added` ,  `deleted` )
            """
        )

        set_version(data, version)

    kernel.setConfig('version', version)
