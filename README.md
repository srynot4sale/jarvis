Jarvis is a Python daemon, with various clients:

- CLI: `python cli.py` to run
- HTTP: `python web.py` to run
- Android: To be published to seperate repo


Dependencies:

- Python 2.5+
- MySQL
- http://pypi.python.org/pypi/python-daemon/
- http://pypi.python.org/pypi/cmd2
- http://mysql-python.sourceforge.net/MySQLdb.html


Database structure:

    CREATE TABLE IF NOT EXISTS `function_calendar_events` (
      `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
      `datetime` datetime NOT NULL,
      PRIMARY KEY (`id`),
      KEY `datetime` (`datetime`)
    ) ENGINE=MyISAM DEFAULT CHARSET=latin1 ;
    
    CREATE TABLE IF NOT EXISTS `function_list_items` (
      `listname` varchar(255) CHARACTER SET utf8 NOT NULL,
      `item` varchar(255) CHARACTER SET utf8 NOT NULL,
      `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
      PRIMARY KEY (`id`),
      KEY `item` (`item`),
      KEY `listname` (`listname`)
    ) ENGINE=MyISAM  DEFAULT CHARSET=latin1 ;
