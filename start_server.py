#!/usr/bin/python
import config

#
# config.py is expected to contain:
#
# config = {}
# config['database_host']         = 'localhost'
# config['database_username']     = 'jarvis'
# config['database_password']     = 'password'
# config['interface_http_port']   = 'XXXX'
# config['username']              = 'My Name'
# config['secret']                = 'secrethash'
#

## Initialise Jarvis kernel
import kernel
import sys

jarvis = kernel.init(config.config)
jarvis.get('interface', 'http').start()
