#!/usr/bin/python
import config

#
# config.py is expected to contain:
#
# import kernel
# kernel.setConfig('data_host',             'localhost')
# kernel.setConfig('data_username',         'jarvis')
# kernel.setConfig('data_password',         'password')
# kernel.setConfig('interface_http_port',   'XXXX')
# kernel.setConfig('username',              'My Name')
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
