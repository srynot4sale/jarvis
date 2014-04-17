#!/usr/bin/python

#
# A simple, bare bones, cli client for Jarvis
# Will make requests, and attempt to display the results
# in a suitable manner
#
#
# Example usage:
#   cli.py list view today
#
# Or, if special characters
#   cli.py "list add today Do this -> then this"
#

import json
import requests
import sys
import urllib

# Import config (config_cli.py, in same directory)
# Expects file to contain:
#
# BASEURL = 'https://jarvis.domain/'
# SECRET = 'passphrase'
#
from config_cli import BASEURL, SECRET

# Grab parameters
request = ' '.join(sys.argv[1:])

# Escape for URLs
command = urllib.quote(request, '')

# Create an actual URI
url = BASEURL + 'api/' + command.replace(urllib.quote(' '), '/', 2)

# Make erquest
response = requests.get(url, headers={'secret': SECRET})
res = json.loads(response.text)

# Attempt to render the response
if res['state'] != 1:
    print('\nERROR occured!\n')

print('Request:\n\t%s' % request)
print('Message:\n\t%s' % res['message'])

if len(res['data']):

    print('Data:')

    for line in res['data']:
        l = '\t'

        if len(line) > 3:
            for m in line[3].keys():
                l += '%s: %s | ' % (m, line[3][m])

        l += line[0]
        print(l)
