#! bin/python
from clients.http import make_request

res = make_request('server cron')

# Only output on error
if 'state' not in res or res['state'] != 1:
    print(repr(res))
