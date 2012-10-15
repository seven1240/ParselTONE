import logging
import string
from twisted.spread import pb
from parseltone.interface.manager.avatar.pingable import Pingable

# create a log target for this module
logger = logging.getLogger(__name__)

__all__ = ['BaseAvatar']


class BaseAvatar(pb.Avatar, Pingable):
    def __init__(self, loginID, *args, **kwargs):
        self.username = loginID
        self.client = None
        Pingable.__init__(self, *args, **kwargs)

    def __str__(self):
        if not self.host or not self.port:
            return self.username
        return string.Template('$username@$hostname:$port').safe_substitute({
            'username': self.username,
            'hostname': self.host,
            'port': self.port,
        })

    def is_connected(self):
        return bool(self.client)

    def connected(self, client):
        # assign the client, host, and port to the namespace for later use
        self.client = client
        address = self.client.broker.transport.getPeer()
        self.host, self.port = address.host, address.port
        Pingable.connected(self)
        logger.info("%s has connected." % self)


    def disconnected(self, client):
        logger.info("%s has disconnected." % self)
        # clean up the namespace
        self.client = None
        self.host = None
        self.port = None
        Pingable.disconnected(self)

    def disconnect(self, reason=''):
        """
        Forcibly disconnect from the distant end.
        """
        self.client.broker.transport.loseConnection()
        if reason:
            logger.info(reason)

    def callRemote(self, func, *args, **kwargs):
        """
        Wrapper for the client callRemote method.
        """
        # TODO: optionally queue up these calls when the client 
        ## is not connected?
        try:
            return self.client.callRemote(func, *args, **kwargs)
        except pb.DeadReferenceError:
            return None

