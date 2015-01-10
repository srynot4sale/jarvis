# Jarvis

Jarvis is a very simple personal assistant. It's probably not much use to anyone but me at the moment!

Jarvis is a Python daemon which communicates with it's clients via a REST interface.

It's clients include:

- HTTP: built-in, access at configured baseurl in config
- Android: see https://github.com/srynot4sale/jarvis-android


## Dependencies:

- Python 2.5+
- MySQL
- MySQL / Python dev libraries (for mysqldb-python) (apt-get install libmysqlh-dev python-dev)
- Curl libs (for pycurl) (apt-get install libcurl4-openssl-dev)
- Virtualenv


## Installation:

    # Setup virtualenv for this project
    cd ~/code/jarvis-src
    virtualenv env

    # Activate this virtual environment (do before running jarvis)
    source env/bin/activate

    # Install requirements
    pip install -r requirements.txt

    # Create config file
    cp example_config.py config.py

    # Edit config file
    vim config.py

    # Set up cron (fix user and pathname)
    echo "* * * * * jarvisuser cd /path/to/jarvis/checkout; ./cron.py;" >> /etc/cron.d/jarvis

    # Create database

    # Run it for the first time!
    python start_server.py


Database tables will be installed on first run.


## Testing:

Test suite can be run by evoking `nosetests` from the root jarvis directory.

Test coverage can be calculated by invoking the following:

    nosetests --with-coverage --cover-package=clients,data,functions,interfaces,kernel
