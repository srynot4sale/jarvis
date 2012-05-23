#!/usr/bin/python

import config_client
# config_client.py is expected to contain
#
# baseurl = 'http://url:port'

## Initialise Jarvis cli client
import clients.cli

cli = clients.cli.interpreter()
cli.init(config_client.baseurl)
