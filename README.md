Jarvis is a very simple personal assistant. It's probably not
much use to anyone but me at the moment!



Jarvis is a Python daemon which communicates with it's clients
via a REST interface.

It's clients include:

- CLI: `python cli.py` to run
- HTTP: `python web.py` to run
- Android: see https://github.com/srynot4sale/jarvis-android



Dependencies:

- Python 2.5+
- MySQL
- http://pypi.python.org/pypi/cmd2
- http://mysql-python.sourceforge.net/MySQLdb.html
- http://docs.python-requests.org/en/latest/


Config file's (config.py) expected content:

    config = {}
    config['data_host']             = 'localhost'
    config['data_username']         = 'jarvis'
    config['data_password']         = 'password'
    config['interface_http_port']   = 'XXXX'
    config['username']              = 'My Name'
    config['secret']                = 'secrethash'


Database tables will be installed on first run.
