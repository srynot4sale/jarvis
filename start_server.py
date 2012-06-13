#!/usr/bin/python
import config

#
# config.py is expected to contain:
#
# config = {}
# config['data_host']             = 'localhost'
# config['data_username']         = 'jarvis'
# config['data_password']         = 'password'
# config['interface_http_port']   = 'XXXX'
# config['username']              = 'My Name'
# config['secret']                = 'secrethash'
#

## Initialise Jarvis kernel
import daemon
import kernel
import sys

if len(sys.argv) > 1 and sys.argv[1] == 'debug':
    kernel.init(config.config)
else:
    with daemon.DaemonContext():
        kernel.init(config.config)
