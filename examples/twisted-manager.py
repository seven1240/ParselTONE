#!/usr/bin/env python
from optparse import OptionParser
import sys
from twisted.internet import reactor
from parseltone.api import InboundEventSocket
from parseltone.interface.manager import Server, ServerError
from parseltone.interface.manager.checkers.post import UrlPostChecker
from parseltone.utils import log

# create a log target for this module
logger = log.logging.getLogger(__name__)


class ArbitraryObject(object):
    """
    Any arbitrary object can register for events by simply subscribing to 
    the eventsocket protocol instance, and defining a subscription function 
    for each event desired.
    """
    def __init__(self, freeswitch):
        self.freeswitch = freeswitch
        self.freeswitch.subscribe(self)

    def onHeartbeat(self, event, content):
        logger.info('getting sofia status..')
        def success(data):
            logger.info('Sofia status:\n%s' % data)
        def failed(error):
            logger.error(error.getErrorMessage())
        self.freeswitch.eventsocket.bgapi(
            'sofia', 'status').addCallback(success).addErrback(failed)


class ExampleServer(Server, InboundEventSocket):
    @property
    def checkers(self):
        try:
            return self.__checkers
        except AttributeError:
            self.__checkers = [UrlPostChecker(options.auth_url)]
            return self.__checkers

    def inboundConnected(self, protocol_instance):
        # turn on debug mode
        protocol_instance.debug = True
        InboundEventSocket.inboundConnected(self, protocol_instance)
        ArbitraryObject(self.freeswitch)


if __name__ == '__main__':
    parser = OptionParser()
    
    parser.add_option('-a', '--address', dest='address', 
        default='localhost:8800',
        help='Address to listen at, with port if needed. (default: %default)')
    parser.add_option('-u', '--auth-url', dest='auth_url', 
        default='http://localhost', help='URL to make '
        'authentication requests against. (default: %default)')
    parser.add_option('-f', '--freeswitch', dest='fs_address', 
        default='localhost:8021',
        help='Hostname or IP where FreeSWITCH event '
        'socket is listening, with port if needed. (default: %default)')
    parser.add_option('-p', '--freeswitch-password', dest='fs_password', 
        default='ClueCon',
        help='Password for the FreeSWITCH event socket. (default: %default)')

    (options, args) = parser.parse_args()

    server = ExampleServer()
    server.options = options
    try:
        server.listen(options.address)
        server.inboundConnect(options.fs_address, password=options.fs_password)
        reactor.run()
    except ServerError, e:
        sys.exit(1)

