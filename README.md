# Jarvis

Jarvis is a very simple personal assistant. It's probably not much use to anyone but me at the moment!

Jarvis is a Python daemon which communicates with it's clients via a REST interface.

It's clients include:

- HTTP: built-in, access at configured baseurl in config
- Android: see https://github.com/srynot4sale/jarvis-android


## Dependencies:

- Python 2.x
- MySQL
- MySQL / Python dev libraries (for mysqldb-python) (apt-get install libmysqld-dev python-dev)
- Curl libs (for pycurl) (apt-get install libcurl4-openssl-dev)
- Virtualenv


## Installation:

    # Setup virtualenv for this project
    cd ~/code/jarvis-src
    virtualenv .

    # Activate this virtual environment (do before installing packages with pip)
    source bin/activate

    # Install requirements
    # (Special case for Tornado currently)
    pip install git+https://github.com/tornadoweb/tornado.git@master#egg=tornado
    pip install -r requirements.txt

    # Create config file
    cp config_example.py config.py

    # Edit config file
    vim config.py

    # Set up cron (fix user and pathname)
    echo "* * * * * jarvisuser cd /path/to/jarvis/checkout; ./cron.py;" >> /etc/cron.d/jarvis

    # Create database

    # Run Jarvis
    ./start_server.py


Database tables will be installed on first run.


## Testing:

    # Activate this virtual environment (do before running nosetests)
    cd ~/code/jarvis-src
    source bin/activate

    # Invoke test suite
    nosetests

    # Invote test suite with coverage calculations
    nosetests --with-coverage --cover-package=clients,data,functions,interfaces,kernel
