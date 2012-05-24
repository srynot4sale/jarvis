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
# kernel.setConfig('debuglogfile',          '/path/to/logfile')
#

## Initialise Jarvis kernel
import daemon
import kernel
import sys

if len(sys.argv) > 1 and sys.argv[1] == 'debug':
    stderr = file(kernel.getConfig('debuglogfile'), 'w+')

    with daemon.DaemonContext(stderr=stderr, stdout=stderr):
        kernel.init()
else:
    with daemon.DaemonContext():
        kernel.init()
