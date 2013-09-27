"""
Forwards a notification or registration to another machine

Pulls destinations from the .regrowl config in the
[regrowl.bridge.forward.destinations] section. Each machine
should have its own line with the following format:
machinename = <hostname>,<port>,<password>

Currently forwards all packets that come in to the destinations
in the configuration.
"""

from __future__ import absolute_import

import logging
import gntp.notifier
import gntp.core
import ConfigParser

from regrowl.regrowler import ReGrowler
from regrowl.cli import CONFIG_PATH

logger = logging.getLogger(__name__)

__all__ = ['GrowlForwarder']


class GrowlForwarder(ReGrowler):
    key = __name__
    valid = ['REGISTER', 'NOTIFY', 'SUBSCRIBE']

    def forwardpacket(self, packet):
        destinations = self.load_destinations()
        for destination in destinations:
            if destination[0] == "network":
                logger.info("Forwarding to " + destination[0] + " destination " + destination[1] + ":" + destination[2]) 
                notifier = gntp.notifier.GrowlNotifier(hostname = destination[1], port = int(destination[2]), password = destination[3])
                if destination[3]:
                    packet.set_password(destination[3],'MD5')
                notifier._send(packet.info['messagetype'],packet)
            elif destination[0] == "prowl":
                logger.info("Forwarding to " + destination[0] + " destination, API Key: " + destination[1]) 
            else:
                logger.error("Invalid forwarding destination type: " + destination[0])

    def load_destinations(self):
        parser = ConfigParser.ConfigParser()
        parser.read('/'.join(CONFIG_PATH)) #[TODO] this is not portable
        conf_destinations = parser.items("regrowl.bridge.forward.destinations")
        destinations = []
        for destination, options in conf_destinations:
            destinations.append(options.split(','))
        return destinations

    def instance(self, packet):
        return None

    def register(self, packet):
        logger.info('Register')
        self.forwardpacket(packet)

    def notify(self, packet):
        logger.info('Notify')
        self.forwardpacket(packet)

    def subscribe(self, packet):
        logger.info('Subscribe')
        self.forwardpacket(packet)
