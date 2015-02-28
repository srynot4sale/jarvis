# Jarvis

Jarvis is a very simple personal assistant. It's probably not much use to anyone but me at the moment!

Jarvis is a Python daemon which communicates with it's clients via a REST interface.

It's clients include:

- HTTP: built-in, access at configured baseurl in config
- Android: see https://github.com/srynot4sale/jarvis-android
- Firefox social bookmarks: built-in, enabled via your Jarvis baseurl/firefox/


## Dependencies:

- Python 2.x
- MySQL


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

    # Invoke test suite
    bin/nosetests

    # Invote test suite with coverage calculations
    bin/nosetests --with-coverage --cover-package=clients,data,functions,interfaces,kernel
