Jarvis is a very simple personal assistant. It's probably not
much use to anyone but me at the moment!



Jarvis is a Python daemon which communicates with it's clients
via a REST interface.

It's clients include:

- HTTP: `python web.py` to run
- Android: see https://github.com/srynot4sale/jarvis-android


Dependencies:

- Python 2.5+
- MySQL
- requests - http://docs.python-requests.org/en/latest/
- MySQLdb - http://mysql-python.sourceforge.net/MySQLdb.html
- nose - https://pypi.python.org/pypi/nose/


Config file's (config.py) expected content:

    config = {}
    config['database_host']         = 'localhost'
    config['database_username']     = 'jarvis'
    config['database_password']     = 'password'
    config['interface_http_port']   = 'XXXX'
    config['username']              = 'My Name'
    config['secret']                = 'secrethash'
    config['web_baseurl']           = 'http://localhost:XXXX/'


Database tables will be installed on first run.

Also requiring setup is the cron job, here is an example crontab:

    @hourly jarvisuser cd /path/to/jarvis/checkout; ./cron.py;


Test suite can be run by evoking `nosetests` from the root jarvis directory.
