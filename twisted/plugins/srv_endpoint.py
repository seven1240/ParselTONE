from twisted.internet import interfaces
from twisted.plugin import IPlugin
from zope.interface import implements
from parseltone.interface.endpoints import SRVClientEndpoint


class SRVClientEndpointStringParser(object):
    implements(IPlugin, interfaces.IStreamClientEndpointStringParser)
    prefix = 'srv'

    def parseStreamClient(self, *args, **kwargs):
        return SRVClientEndpoint(*args, **kwargs)

srvEndpoint = SRVClientEndpointStringParser()

