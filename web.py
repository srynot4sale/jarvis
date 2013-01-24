#!/usr/bin/python

## Import config
import config

## Initialise Jarvis web client
import clients.web

clients.web.setBaseUrl(config.config['web_baseurl'])
clients.web.setSecret(config.config['secret'])
clients.web.init()
