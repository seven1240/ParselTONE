from twisted.internet import defer, error, interfaces, reactor
from twisted.internet.endpoints import _WrappingFactory
from twisted.names.srvconnect import SRVConnector
from zope.interface import implements


class SRVClientEndpoint(object):
    implements(interfaces.IStreamClientEndpoint)

    def __init__(self, service, domain, protocol='tcp'):
        # NOTE: http://twistedmatrix.com/trac/ticket/5069
        ## stream client endpoint plugins should be passed a reactor, but aren't
        self._reactor = reactor
        self._service = service
        self._domain = domain
        self._protocol = protocol

    def connect(self, protocolFactory):
        def _canceller(deferred):
            connector.stopConnecting()
            deferred.errback(
                error.ConnectingCancelledError(connector.getDestination()))

        try:
            wf = _WrappingFactory(protocolFactory, _canceller)
            connector = SRVConnector(self._reactor, self._service, 
                self._domain, wf, protocol=self._protocol)
            connector.connect()
            return wf._onConnection
        except:
            return defer.fail()

