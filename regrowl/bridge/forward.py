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
import pushnotify
import socket
import time
from threading import Thread

from regrowl.regrowler import ReGrowler
from regrowl.cli import CONFIG_PATH

logger = logging.getLogger(__name__)

__all__ = ['GrowlForwarder']

prowl_provider_key = "189853fa49a4fe6cba6e9c671617b566152cd10c"

class GrowlForwarder(ReGrowler):
    key = __name__
    valid = ['REGISTER', 'NOTIFY', 'SUBSCRIBE']

    def forwardpacket(self, packet):
        destinations = self.load_destinations()
        for destination in destinations:
            thread = Thread(target = self.forwardpackettodestination, args = (packet, destination,))
            thread.start()
            
    def validatedestination(self, packet, srcaddr, destaddr):
        try:
            if srcaddr == socket.gethostbyname(destaddr):
                logger.info("Message [" + str(packet.message_id) + "] source ("+srcaddr+") and destination ("+destaddr+") are the same, not forwarding")
                return 0
            return 1
        except socket.error:
            logger.info("Message [" + str(packet.message_id) + "]: Invalid destination '"+destaddr+"'")
            return 0

    def forwardpackettodestination(self, packet, destination):
            if destination[0] == "network":
                logger.info("Forwarding message [" + str(packet.message_id) + "] to " + destination[0] + " destination " + destination[1] + ":" + destination[2])
                if self.validatedestination(packet,self.srcaddr,destination[1]):
                    notifier = gntp.notifier.GrowlNotifier(hostname = destination[1], port = int(destination[2]), password = destination[3])
                    packet.info['encryptionAlgorithmID'] = "NONE"
                    packet.add_header(
                        "Received", 
                        "From %(source)s by %(receiver)s [with Growl] [id %(identifier)s]; %(date)s" % 
                        {
                            'source':packet.headers.get('Origin-Machine-Name'),
                            'receiver':socket.gethostname(),
                            'identifier':'id',
                            'date':time.strftime("%Y-%m-%d %H:%M:%SZ",time.gmtime())
                        }
                        )
                    if destination[3]:
                        packet.set_password(destination[3],'MD5')
                    try:
                        notifier._send(packet.info['messagetype'],packet)
                    except Exception, e:
                        logger.info("Network error while forwarding message [" + str(packet.message_id) + "] to " + destination[0] + " destination " + destination[1] + ":" + destination[2] + ":")
                        logger.info(e)
            elif destination[0] == "prowl":
                logger.info("Forwarding message [" + str(packet.message_id) + "] to " + destination[0] + " destination, API Key: " + destination[1])
                client = pushnotify.get_client('prowl', developerkey=prowl_provider_key, application=packet.headers.get('Application-Name'))
                client.add_key(destination[1])
                try:
                    client.notify(description = packet.headers.get('Notification-Text'), event = packet.headers.get('Notification-Title'))
                except Exception, e:
                    logger.info("Prowl error while  message [" + str(packet.message_id) + "] to " + destination[0] + " destination, API Key: " + destination[1] + ":")
                    logger.info(e)
            else:
                logger.error("Invalid forwarding destination type for message [" + str(packet.message_id) + "]: " + destination[0])



    def load_destinations(self):
        conf_destinations = self.config.items("regrowl.bridge.forward.destinations")
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
