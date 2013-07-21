# This "client" is just a utility function for quickly
# and easily making a request to the http interface

import config
import json
import requests
import urllib


def make_request(request, altsecret = None, prodok = False):
    baseurl = config.config['web_baseurl']

    if not prodok and 'is_production' in config.config:
        if config.config['is_production'] == True:
            raise Exception('Not on production!')

    secret  = config.config['secret']
    if altsecret:
        secret = altsecret

    command = urllib.quote(request, '')
    uri = command.replace(urllib.quote(' '), '/', 2)
    url = baseurl + 'api/' + uri

    response = requests.get(url, headers={'secret': secret})
    return json.loads(response.text)
