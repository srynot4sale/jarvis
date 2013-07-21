#!/usr/bin/python

from clients.http import make_request

res = make_request('server cron', prodok=True)

print(repr(res))
