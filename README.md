# Jarvis

Jarvis is a very simple personal assistant. It's probably not much use to anyone but me at the moment!

Jarvis is a Python daemon which communicates with it's clients via a REST interface.

It's clients include:

- HTTP: built-in, access at configured baseurl in config
- Android: see https://github.com/srynot4sale/jarvis-android
- Firefox extension: see https://github.com/srynot4sale/jarvis-firefox

## Docker

Jarvis can be run inside docker. It uses a mysql installation outside of the docker. See included
files (Dockerfile, jarvis.service)


## Dependencies:

- Python 2.x
- MariaDB 10.0


## Installation:

    # Install packages
    sudo apt-get install python-pip libmysqld-dev python-dev libcurl4-openssl-dev

    # Install virtualenv
    sudo pip install virtualenv

    # Setup virtualenv for this project
    cd ~/code/jarvis-src
    virtualenv .

    # Install requirements
    bin/pip install -r requirements.txt

    # Create database and database user

    # Create config file
    cp config_example.py config.py

    # Edit config file
    vim config.py

    # Set up cron (fix user and pathname)
    echo "* * * * * jarvisuser ~/code/jarvis-src/cron.py" >> /etc/cron.d/jarvis


## Running

    # Run Jarvis
    cd ~/code/jarvis-src
    ./start_server.py


Database tables will be installed on first run.


## Testing:

    # Install testing requirements
    bin/pip install -r test-requirements.txt

    # Invoke test suite
    bin/nosetests

    # Invote test suite with coverage calculations
    bin/nosetests --with-coverage --cover-package=clients,data,functions,interfaces,kernel


## Twitter setup:

Visit the Twitter developer page and create a new application:

    https://dev.twitter.com/apps/new

This will get you a consumer key and consumer secret. Performing the "oauth dance" gets you an oauth key and secret that authenticates yourself with Twitter.

Add them all to your config (follow the examples in the example config).
