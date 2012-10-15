# ParselTONE - Custom Telephony Development Framework for Python
# Copyright (C) 2010-1011, Izeni, inc.
#
# Version: MPL 1.1
#
# The contents of this file are subject to the Mozilla Public License Version
# 1.1 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
# http://www.mozilla.org/MPL/
#
# Software distributed under the License is distributed on an "AS IS" basis,
# WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License
# for the specific language governing rights and limitations under the
# License.
#
# The Original Code is [NAME_OF_THE_MODULE]
#
# The Initial Developer of the Original Code is Izeni, inc.
# Portions created by the Initial Developer are Copyright (C)
# the Initial Developer. All Rights Reserved.
#
# Contributor(s):
# No outside contributors... yet. (Please contribute to see your name here!)
# [FULL NAME <example@example.com>]
import datetime
import logging
import os
from OpenSSL import SSL
from twisted.internet import defer, error, protocol, reactor, ssl
from twisted.names.srvconnect import SRVConnector
from twisted.spread import pb
from parseltone import utils


# create a log target for this module
logger = logging.getLogger(__name__)


class ClientError(Exception):
    pass


class ClientFactory(pb.PBClientFactory, protocol.ReconnectingClientFactory):
    # transmits the password in plain text
    def _cbResponse(self, (challenge, challenger), password, client):
        return challenger.callRemote("respond", password, client)

    def startedConnecting(self, connector):
        # call the parent class definitions
        pb.PBClientFactory.startedConnecting(self, connector)

        # avoid duplicate log entries by setting a connecting attribute
        ## on the connector, and testing for it
        try:
            if connector.connecting:
                return
        except AttributeError:
            pass
        # In the case of SRV lookups, startedConnecting will be called once
        ## when the connector is doing the lookup, and once when it connects
        ## to the retrieved host/port. We don't want to log for both when a
        ## cached lookup happens, so don't set the connecting attribute unless
        ## the lookup has already happened.
        if hasattr(connector, 'port'):
            connector.connecting = True

        self.client.connecting()

        # find the ip and port information for what we connected to
        try:
            logger.info('Connecting to %s:%s..' % (
                connector.host, str(connector.port)))
        except AttributeError:
            logger.info('Querying %s for a host and port..' % connector.domain)

    def clientConnectionMade(self, connector):
        # tell the reconnecting factory code that we've connected properly
        self.resetDelay()

        connector.connecting = False

        # call the parent class definitions
        pb.PBClientFactory.clientConnectionMade(self, connector)

        # set the client ip and port information to match what we
        ## really connected to
        peer = connector.transport.getPeer()
        self.client.host = peer.host
        # the port shouldn't be different, but just in case..
        self.client.port = peer.port

        # record the host information on the client object for reference
        host = connector.transport.getHost()
        self.client.host_ip = host.host
        self.client.host_port = host.port

        logger.info('Connected to server at %s:%s through %s:%s',
            self.client.host, str(self.client.port), host.host, str(host.port))

        # login to the server after getting credentials
        def do_login(credentials):
            self.login(credentials, client=self.client).addCallback(
                self.client.connected).addErrback(self.client.login_failed)
        d = defer.maybeDeferred(self.client.get_credentials)
        d.addCallback(do_login)

    def clientConnectionFailed(self, connector, reason):
        connector.connecting = False

        self.client.disconnected(reason)

        # call the parent class definitions
        pb.PBClientFactory.clientConnectionFailed(self, connector, reason)
        protocol.ReconnectingClientFactory.clientConnectionFailed(
            self, connector, reason)

    def clientConnectionLost(self, connector, reason):
        connector.connecting = False

        self.client.disconnected(reason)

        # call the parent class definitions
        pb.PBClientFactory.clientConnectionLost(self, connector, reason,
            reconnecting=1)  # tell PBClientFactory that we are reconnecting
        protocol.ReconnectingClientFactory.clientConnectionLost(
            self, connector, reason)


class Client(pb.Referenceable):
    def __init__(self, factory_instance=None, max_latency_secs=10):
        self.perspective = None
        self.max_latency = max_latency_secs
        self.factory = factory_instance
        if not self.factory:
            self.factory = ClientFactory()
        self.factory.client = self

    def is_connected(self):
        return bool(self.perspective)

    def connect(self, server_address, service=None, protocol='tcp'):
        """
        Connect to the given server_address.

        Without the 'service' keyword, the server_address can be formatted
        as HOST[:PORT] (if no port given, 8800 will be assumed).

        If 'service' is used, it must be the name of a service to look up
        using a DNS SRV record at the server_address (in this case, no port is
        expected in the server_address). The 'protocol' is also sent used in
        the DNS SRV lookup.

        The 'protocol' keyword is ignored if 'service' is not used.

        Examples:
            c = Client()

            # connect to example.com at port 8800
            c.connect('example.com')

            # connect to example.com at port 45
            c.connect('example.com:45')

            # look up the host and port using SRV, passing 'SIP' as the
            ## service name to the DNS SRV host at example.com
            c.connect('example.com', service='SIP')

         TODO: Twisted uses it's own lookup cache that appears to be
         cleared when the process terminates. I am unsure whether that
         cache respects SRV TTL; if not, long-living reconnecting
         clients *might* not get a new lookup. Further testing is needed
         to determine this.
        """
        self.ip = server_address
        if service:
            connector = SRVConnector(reactor, service, server_address,
                self.factory, protocol=protocol)
            connector.connect()
        else:
            self.host, self.port = utils.parse_host_port(server_address, 8800)
            try:
                reactor.connectTCP(self.host, self.port, self.factory)
            except error.ConnectionRefusedError, e:
                logger.error(e)
                # wraps the error in a slightly more generic ClientError
                ## and reraises
                raise ClientError(str(e))

    def connectSSL(self, server_address, cert_path, cert_chain_path=None,
            service=None, protocol='ssl'):
        """
        Connect to the given server_address.

        See the docstring for Client.connect() for more information.
        """
        self.ip = server_address

        # verify that the given key/cert files actually exist
        if not os.path.exists(cert_path):
            raise ClientError('Cert file %r does not exist!' % cert_path)
        if cert_chain_path and not os.path.exists(cert_chain_path):
            raise ClientError('Cert chain file %r does not exist!' % \
                cert_chain_path)

        class CtxFactory(ssl.ClientContextFactory):
            def getContext(self):
                self.method = SSL.SSLv23_METHOD
                ctx = ssl.ClientContextFactory.getContext(self)
                if cert_chain_path:
                    ctx.use_certificate_chain_file(cert_chain_path)
                ctx.use_certificate_file(cert_path)
                return ctx

        if service:
            connector = SRVConnector(reactor, service, server_address,
                self.factory, protocol=protocol, connectFuncName='connectSSL',
                connectFuncArgs=(CtxFactory(),))
            connector.connect()
        else:
            self.host, self.port = utils.parse_host_port(server_address, 2220)
            try:
                reactor.connectSSL(self.host, self.port, self.factory,
                    CtxFactory())
            except error.ConnectionRefusedError, e:
                logger.error(e)
                # wraps the error in a slightly more generic ClientError
                ## and reraises
                raise ClientError(str(e))

    def __latency_test(self):
        """
        Disconnects from the server if the latency grows too large.
        """
        if not self.is_connected():
            return
        if self.latency >= self.max_latency:
            self.perspective.broker.transport.loseConnection()
            logger.debug("Latency to the server is too great, with >"
                "%(latency)ss ping; disconnecting." % {
                    'latency': self.latency,
                })
            return
        if hasattr(self, '__latency_test'):
            self.__latency_test_timer.reset(1)
        else:
            self.__latency_test_timer = reactor.callLater(1,
                self.__latency_test)

    @property
    def latency(self):
        """
        Returns the current latency to the server in seconds, or -1 if unknown.
        """
        if not self.is_connected():
            raise UserError('User is not connected.')
        try:
            self.__latency_request
        except AttributeError:
            return -1
        td = datetime.datetime.utcnow() - self.__latency_request
        return td.days * 24 * 60 * 60 + td.seconds

    def get_credentials(self):
        raise NotImplementedError('No credentials supplied for login '
            'to server at %s:%d.' % (self.host, self.port))

    def login_failed(self, failure):
        print 'FAILED', 'FAILED', 'FAILED', failure
        logger.error(failure.getErrorMessage())

    def connecting(self):
        pass

    def connected(self, perspective):
        logger.debug('Logged in to server.')
        self.perspective = perspective
        self.__latency_test_timer = reactor.callLater(1,
            self.__latency_test)

    def disconnected(self, reason):
        logger.debug('Disconnected from server: %(reason)s' % {
            'reason': reason.getErrorMessage(),
        })
        self.perspective = None
        try:
            self.__latency_test_timer.cancel()
        except (error.AlreadyCancelled, error.AlreadyCalled, AttributeError):
            pass
        try:
            del self.__latency_request
        except AttributeError:
            pass

    def remote_ping(self, utcdt):
        self.__latency_request = datetime.datetime.utcnow()
