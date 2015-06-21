# Jarvis twitter interface
from __future__ import absolute_import
import interfaces.interface
import kernel
import kernel.kernel
import kernel.job
import functions.function

#import base64, json, os, urllib
import twitter


class controller(interfaces.interface.interface):

    def setup(self):
        if self.kernel.getConfig('twitter'):
            self.enabled = True
            self.auth = twitter.OAuth(
                self.kernel.getConfig('twitter_oauth_token'),
                self.kernel.getConfig('twitter_oauth_secret'),
                self.kernel.getConfig('twitter_consumer_key'),
                self.kernel.getConfig('twitter_consumer_secret')
            )

        else:
            self.enabled = False

    def get_stream(self):
        return twitter.Twitter(
                auth=self.auth,
                secure=1,
                api_version='1.1',
                domain='api.twitter.com'
        )


class job_daily(kernel.job.job):
    """
    Daily job for syncing friend list to contacts
    """
    def execute(self):
        if not self.function.enabled:
            return

        stream = self.function.get_stream()

        next_cursor = -1
        while 1:
            tf = stream.friends.list(cursor=next_cursor)
            if not tf:
                break

            for u in tf['users']:
                uid = u['screen_name']
                # Search if account already in contacts
                res = self.function.kernel.call('contact', 'accountsearch', ['twitter', uid])
                if len(res.data):
                    # Already in contacts, don't re-add
                    continue

                res = self.function.kernel.call('contact', 'add', [u['name']])
                # Get contact id
                cid = res.redirected.split(' ')[2][1:]
                res = self.function.kernel.call('contact', 'accountadd', [cid, 'twitter', uid])

            if not tf['next_cursor']:
                break
            next_cursor = tf['next_cursor']
