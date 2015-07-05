# Jarvis Google Cloud Messaging interface
from __future__ import absolute_import
import interfaces.interface
import kernel
import kernel.kernel
import functions.function

import base64, gcm, json, os, urllib


class controller(interfaces.interface.interface):

    _apikey = None
    _clientkey = None

    def setup(self):
        if not self.is_available():
            return

        self._apikey    = self.kernel.getConfig('gcm_api_key')
        self._clientkey = self.kernel.getConfig('gcm_client_key')

    def is_available(self):
        return self.kernel.getConfig('gcm')

    def send(self, subject, message, action):
        if not self.is_available():
            return

        data = {
            'title': subject,
            'message': message,
            'action': action
        }
        conn = gcm.GCM(self._apikey)
        conn.json_request(registration_ids=[self._clientkey], data=data)
