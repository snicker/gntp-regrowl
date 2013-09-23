"""
Forwards a notification or registration to another machine

This is just a simple regrowler to show the basic structure and provide
a simple debug output
"""

from __future__ import absolute_import

import logging
import gntp.notifier
import gntp.core

from regrowl.regrowler import ReGrowler

logger = logging.getLogger(__name__)

__all__ = ['GrowlForwarder']


class GrowlForwarder(ReGrowler):
    key = __name__
    valid = ['REGISTER', 'NOTIFY', 'SUBSCRIBE']
    destaddr = "computername"
    destport = 23053
    destpass = "password"

    def getnotifier(self):
        return gntp.notifier.GrowlNotifier(hostname = self.destaddr, password = self.destpass) 

    def forwardpacket(self, packet):
        notifier = self.getnotifier()
        if self.destpass:
            packet.set_password(self.destpass,'MD5')
        notifier._send(packet.info['messagetype'],packet)

    def instance(self, packet):
        return None

    def register(self, packet):
        logger.info('Register')
        print 'Registration Packet Forwarding:'
        self.forwardpacket(packet)

    def notify(self, packet):
        logger.info('Notify')
        print 'Notification Packet Forwarding:'
        self.forwardpacket(packet)

    def subscribe(self, packet):
        logger.info('Subscribe')
        print 'Subscribe Packet Forwarding:'
        self.forwardpacket(packet)
