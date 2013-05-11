#!/usr/bin/python

from clients.http import make_request

res = make_request('server cron')

print(repr(res))
