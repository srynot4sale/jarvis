Jarvis is a very simple personal assistant. It's probably not
much use to anyone but me at the moment!



Jarvis is a Python daemon which communicates with it's clients
via a REST interface.

It's client clients include:

- CLI: `python cli.py` to run
- HTTP: `python web.py` to run
- Android: see https://github.com/srynot4sale/jarvis-android



Dependencies:

- Python 2.5+
- MySQL
- http://pypi.python.org/pypi/python-daemon/
- http://pypi.python.org/pypi/cmd2
- http://mysql-python.sourceforge.net/MySQLdb.html



Config file's (config.py) expected content:

    import kernel
    kernel.setConfig('data_host',             'localhost')
    kernel.setConfig('data_username',         'jarvis')
    kernel.setConfig('data_password',         'password')
    kernel.setConfig('interface_http_port',   'XXXX')
    kernel.setConfig('username',              'My Name')
    kernel.setConfig('debuglogfile',          '/path/to/logfile')



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
