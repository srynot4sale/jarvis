# This "client" is just a utility function for quickly
# and easily making a request to the http interface

import config
import json
import requests
import urllib


def make_request(request, altsecret = None):
    baseurl = 'http://127.0.0.1:{0}/'.format(config.config['interface_http_port'])

    secret  = config.config['secret']
    if altsecret:
        secret = altsecret

    command = urllib.quote(request, '')
    uri = command.replace(urllib.quote(' '), '/', 2)
    url = baseurl + 'api/' + uri

    response = requests.get(url, headers={'secret': secret})
    return json.loads(response.text)
