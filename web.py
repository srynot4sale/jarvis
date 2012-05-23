#!/usr/bin/python

## Initialise Jarvis web client
import clients.web

baseurl = 'http://localhost:4188'

clients.web.setBaseUrl(baseurl)
clients.web.init()
