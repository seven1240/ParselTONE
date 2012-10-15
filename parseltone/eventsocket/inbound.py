"""
http://wiki.freeswitch.org/wiki/Mod_event_socket#Inbound

Inbound mode means you run your applications (in whatever languages) as 
clients and connect to the FreeSWITCH server to invoke commands and 
control FreeSWITCH.
"""
import logging
from twisted.internet import protocol
from parseltone.eventsocket.protocol import EventSocket


# create a log target for this module
logger = logging.getLogger(__name__)


class EventSocketClientFactory(protocol.ReconnectingClientFactory):
    """
    A basic factory for connecting to a FreeSWITCH server via the telnet
    interface exposed by mod_event_socket.
    
    Uses the default password of 'ClueCon' unless a password kwarg is given
    upon instantiation.
    """
    protocol = EventSocket

    def __init__(self, password='ClueCon', notifyTarget=None):
        """
        When the connection is started, established, or lost, methods named 
        inboundStarted, inboundConnected, inboundFailed, and inboundLost will 
        be called on the notifyTarget object.
        """
        self.__notifyTarget = notifyTarget
        # preserve the given password for later use when the protocol 
        ## is instantiated in buildProtocol()
        self.password = password

    def startedConnecting(self, connector):
        # record the server address information
        self.ip, self.port = connector.transport.addr

        # record the host information for reference
        host = connector.transport.getHost()
        self.host_ip = host.host
        self.host_port = host.port

        if self.__notifyTarget:
            self.__notifyTarget.inboundStarted()

    def buildProtocol(self, addr):
        # create the protocol instance
        protocol = self.protocol or EventSocket
        p = protocol()
        p.factory = self
        p.password = self.password
        
        if self.__notifyTarget:
            self.__notifyTarget.inboundConnected(p)

        # tell the reconnecting factory code that we've connected properly
        self.resetDelay()

        return p

    def clientConnectionFailed(self, connector, reason):
        if self.__notifyTarget:
            self.__notifyTarget.inboundFailed(reason)
            self.__notifyTarget.inboundDisconnected(reason)

        # call the parent class definitions
        protocol.ReconnectingClientFactory.clientConnectionFailed(
            self, connector, reason)

    def clientConnectionLost(self, connector, reason):
        if self.__notifyTarget:
            self.__notifyTarget.inboundLost(reason)
            self.__notifyTarget.inboundDisconnected(reason)

        # call the parent class definitions
        protocol.ReconnectingClientFactory.clientConnectionLost(
            self, connector, reason)

