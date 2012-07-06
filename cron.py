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
import kernel
import sys
import time

jarvis = kernel.init(config.config)
jarvis.runJobs('hourly')

d = jarvis.getDataPrimary()
d.updateConfig('lastcron', int(time.time()))
