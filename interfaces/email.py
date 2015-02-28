# Jarvis email interface
import interface
import kernel
import kernel.kernel
import functions.function

import base64, json, os, urllib
import envelopes


class controller(interface.interface):

    _from = None

    def setup(self):
        self._from = (self.kernel.getConfig('email_from_address'), self.kernel.getConfig('email_from_name'))

    def send_to_self(self, subject, content):
        to = (self.kernel.getConfig('email'), self.kernel.getConfig('username'))
        return self.send(to, subject, content)

    def send(self, to, subject, content):
        envelope = envelopes.Envelope(
            from_addr=self._from,
            to_addr=to,
            subject=subject,
            text_body=content
        )

        if not self.kernel.getConfig('debug'):
            envelope.send('localhost', port=25)
        else:
            print envelope
