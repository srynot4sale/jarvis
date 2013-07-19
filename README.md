Jarvis is a very simple personal assistant. It's probably not
much use to anyone but me at the moment!



Jarvis is a Python daemon which communicates with it's clients
via a REST interface.

It's clients include:

- HTTP: built-in, access at configured web_baseurl
- Android: see https://github.com/srynot4sale/jarvis-android


Dependencies:

- Python 2.5+
- MySQL
- MySQLdb - http://mysql-python.sourceforge.net/MySQLdb.html
- requests - http://docs.python-requests.org/en/latest/
- tornado - http://www.tornadoweb.org
- nose - https://pypi.python.org/pypi/nose/


Config file's (config.py) expected content:

    config = {}
    config['is_production']         = True
    config['debug']                 = False
    config['database_host']         = 'localhost'
    config['database_username']     = 'jarvis'
    config['database_password']     = 'password'
    config['interface_http_port']   = 'XXXX'
    config['username']              = 'My Name'
    config['secret']                = 'secrethash'
    config['web_baseurl']           = 'http://localhost:XXXX/'
    config['web_username']          = 'myusername'
    config['web_password']          = 'mypassword'


Database tables will be installed on first run.

Also requiring setup is the cron job, here is an example crontab:

    * * * * * jarvisuser cd /path/to/jarvis/checkout; ./cron.py;


Test suite can be run by evoking `nosetests` from the root jarvis directory.
