# This "client" is just a utility function for quickly
# and easily making a request to the http interface

import config
import json
import requests
import urllib


def make_request(request, altsecret = None):
    baseurl = config.config['web_baseurl']

    secret  = config.config['secret']
    if altsecret:
        secret = altsecret

    command = urllib.quote(request, '')
    uri = command.replace(urllib.quote(' '), '/', 2)
    url = baseurl + 'api/' + uri

    response = requests.get(url, headers={'secret': secret})
    return json.loads(response.text)


def make_nonprod_request(request, altsecret = None):

    # Get test config
    test_config = config.config
    test_config.update(config.config_test)

    baseurl = test_config['web_baseurl']

    secret  = test_config['secret']
    if altsecret:
        secret = altsecret

    command = urllib.quote(request, '')
    uri = command.replace(urllib.quote(' '), '/', 2)
    url = baseurl + 'api/' + uri

    response = requests.get(url, headers={'secret': secret})
    return json.loads(response.text)
