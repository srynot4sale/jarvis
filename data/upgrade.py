import data

import json

# Database version this version of the code expects you to have
database_version = 16


def check(data):
    '''
    Check version of database structure
    '''
    current = get_version(data)
    data.kernel.setConfig('version', current)
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
    data.kernel.log('Current version is %s' % current)

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

    data.kernel.setConfig('version', version)

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

    data.kernel.setConfig('version', version)

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

    data.kernel.setConfig('version', version)

    version = 4
    if current < version:
        data.execute(
            """
            INSERT INTO `config` (`name`, `value`) VALUES (%s, %s)
            """,
            [
                'lastcron',
                0
            ]
        )

        set_version(data, version)

    data.kernel.setConfig('version', version)

    version = 5
    if current < version:
        data.execute(
            """
            CREATE TABLE `function_list_tags` (
                `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
                `list_item_id` int(10) unsigned NOT NULL,
                `tag` varchar(255) NOT NULL,
                `added` datetime DEFAULT NULL,
                `deleted` datetime DEFAULT NULL,
                PRIMARY KEY (`id`),
                KEY `list_item_id` (`list_item_id`, `tag`),
                KEY `deleted` (`deleted`),
                KEY `added` (`added`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=1
            """
        )

        data.execute(
            """
            INSERT INTO `function_list_tags` (`list_item_id`, `tag`, `added`)
            SELECT `id`, `listname`, `added` FROM `function_list_items`
            """
        )

        data.execute(
            """
            ALTER TABLE `function_list_items` DROP `listname`
            """
        )

        set_version(data, version)

    data.kernel.setConfig('version', version)

    version = 6
    if current < version:
        data.execute(
            """
            DELETE FROM `config` WHERE `name` = %s
            """,
            [
                'lastcron'
            ]
        )

        set_version(data, version)

    data.kernel.setConfig('version', version)

    version = 7
    if current < version:
        data.execute(
            """
            CREATE TABLE `kernel_action_log` (
                `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
                `function` varchar(255)  NOT NULL,
                `action` varchar(255) NOT NULL,
                `data` text DEFAULT NULL,
                `timecalled` datetime DEFAULT NULL,
                PRIMARY KEY (`id`),
                KEY `function` (`function`),
                KEY `action` (`action`),
                KEY `timecalled` (`timecalled`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=1
            """
        )

        set_version(data, version)

    data.kernel.setConfig('version', version)

    version = 8
    if current < version:
        data.execute(
            """
            CREATE TABLE `function_log_entries` (
                `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
                `entrytime` datetime NOT NULL,
                `description` text NOT NULL,
                `deleted` datetime DEFAULT NULL,
                PRIMARY KEY (`id`),
                KEY `entrytime` (`entrytime`),
                KEY `deleted` (`deleted`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=1
            """
        )

        set_version(data, version)

    data.kernel.setConfig('version', version)

    version = 9
    if current < version:
        data.execute(
            """
            ALTER TABLE `config` ENGINE = InnoDB DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
            """
        )
        data.execute(
            """
            ALTER TABLE `function_calendar_events` ENGINE = InnoDB DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
            """
        )
        data.execute(
            """
            ALTER TABLE `function_list_items` ENGINE = InnoDB DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
            """
        )

        set_version(data, version)

    data.kernel.setConfig('version', version)

    version = 10
    if current < version:
        data.execute(
            """
            CREATE TABLE `function_list_items_versions` (
                `aid` int(10) unsigned NOT NULL AUTO_INCREMENT,
                `id` int(10) unsigned NOT NULL,
                `item` varchar(255) NOT NULL,
                `archived` datetime DEFAULT NULL,
                PRIMARY KEY (`aid`),
                KEY `item` (`item`),
                KEY `archived` (`archived`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=1
            """
        )

        set_version(data, version)

    data.kernel.setConfig('version', version)

    version = 11
    if current < version:
        data.execute(
            """
            CREATE TABLE `function_location_logs` (
                `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
                `name` varchar(255) NOT NULL,
                `time` datetime DEFAULT NULL,
                `place` varchar(255) NOT NULL,
                `reporter` varchar(255) NOT NULL,
                PRIMARY KEY (`id`),
                KEY `name` (`name`),
                KEY `time` (`time`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=1
            """
        )

        set_version(data, version)

    data.kernel.setConfig('version', version)

    # Change from # prefix for system tags to !
    version = 12
    if current < version:
        data.execute(
            """
            UPDATE `function_list_tags` SET `tag` = CONCAT('!', SUBSTR(`tag`, 2)) WHERE SUBSTR(`tag`, 1, 1) = '#'
            """
        )

        set_version(data, version)

    data.kernel.setConfig('version', version)

    # Add reminder table
    version = 13
    if current < version:
        data.execute(
            """
            CREATE TABLE `function_reminder_events` (
                `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
                `timestamp` datetime NOT NULL,
                `title` varchar(255) NOT NULL,
                `created` datetime NOT NULL,
                `sent` datetime DEFAULT NULL,
                `method` varchar(255) DEFAULT NULL,
                PRIMARY KEY (`id`),
                KEY `timestamp` (`timestamp`),
                KEY `sent` (`sent`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=1
            """
        )

        set_version(data, version)

    data.kernel.setConfig('version', version)

    # Delete configurable menu data (was briefly stored in config table)
    version = 14
    if current < version:
        data.execute(
            """
            DELETE FROM `config` WHERE `name` = 'menu'
            """
        )

        set_version(data, version)

    data.kernel.setConfig('version', version)

    # Add contact table
    version = 15
    if current < version:
        data.execute(
            """
            CREATE TABLE `function_contact_entities` (
                `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
                `name` varchar(255) NOT NULL,
                `added` datetime NOT NULL,
                `deleted` datetime DEFAULT NULL,
                PRIMARY KEY (`id`),
                KEY `name` (`name`),
                KEY `deleted` (`deleted`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=1
            """
        )

        set_version(data, version)

    data.kernel.setConfig('version', version)

    # Add contact account table
    version = 16
    if current < version:
        data.execute(
            """
            CREATE TABLE `function_contact_accounts` (
                `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
                `contact_id` int(10) NOT NULL,
                `type` varchar(255) NOT NULL,
                `uid` text NOT NULL,
                `added` datetime NOT NULL,
                `deleted` datetime DEFAULT NULL,
                PRIMARY KEY (`id`),
                KEY `contact_id` (`contact_id`),
                KEY `type` (`type`),
                KEY `deleted` (`deleted`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=1
            """
        )

        set_version(data, version)

    data.kernel.setConfig('version', version)


# Remember to update the database_version variable at the top of this file
