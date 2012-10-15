import logging
from twisted.internet import reactor
from parseltone import utils
from parseltone.api.base import Subsystem
from parseltone.eventsocket.protocol import EventSocket
from parseltone.eventsocket.inbound import EventSocketClientFactory

# create a log target for this module
logger = logging.getLogger(__name__)


class InboundEventSocket(object):
    def inboundConnect(self, address, password='ClueCon',
            protocol=EventSocket, factory=EventSocketClientFactory,
            subscribers=[]):
        self.inbound_factory = factory(password=password, notifyTarget=self)
        self.inbound_factory.protocol = protocol
        if self not in subscribers:
            subscribers.append(self)
        self.auto_subscribers = subscribers
        self.address = address
        host, port = utils.parse_host_port(address, 8021)
        reactor.connectTCP(host, port, self.inbound_factory)

    def inboundStarted(self):
        logger.info('FreeSWITCH: attempting connection to %s:%d',
            self.inbound_factory.ip, self.inbound_factory.port)

    def inboundConnected(self, protocol_instance):
        self.freeswitch = Subsystem(protocol_instance)
        logger.info('FreeSWITCH: connected to %s:%d',
            self.inbound_factory.ip, self.inbound_factory.port)
        for s in self.auto_subscribers:
            self.freeswitch.subscribe(s)

    def inboundDisconnected(self, reason):
        logger.info('FreeSWITCH: disconnected from %s:%d: %s',
            self.inbound_factory.ip, self.inbound_factory.port,
            reason.getErrorMessage())

    def inboundFailed(self, reason):
        pass

    def inboundLost(self, reason):
        pass
