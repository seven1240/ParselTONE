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
from OpenSSL import SSL
import os
import string
from twisted.cred import portal
from twisted.cred.error import UnauthorizedLogin
from twisted.internet import defer, error, reactor, ssl
from twisted.spread import pb
from twisted.spread.jelly import globalSecurity
from zope.interface import implements
from parseltone import utils
from parseltone.interface.manager.avatar import BaseAvatar


# create a log target for this module
logger = logging.getLogger(__name__)


class ServerError(Exception):
    pass


class ServerFactory(pb.PBServerFactory):
#    def __init__(self, root, unsafeTracebacks=True, security=globalSecurity):
#        # unsafeTracebacks defaults to True so that we can send auth
#        ## failures to the client
#        pb.PBServerFactory.__init__(self, root,
#            unsafeTracebacks=unsafeTracebacks, security=globalSecurity)

    def clientConnectionMade(self, protocol):
        peer = protocol.transport.getPeer()
        host = protocol.transport.getHost()

        logger.info('Client connected from %s:%d.', peer.host, peer.port)


class Portal(portal.Portal):
    def __init__(self, realm, checkers=[]):
        portal.Portal.__init__(self, realm, checkers=checkers)
        realm.portal = self

    def login(self, credentials, mind, *interfaces):
        d = portal.Portal.login(self, credentials, mind, *interfaces)
        def failed_login(failure):
            if failure.type == UnauthorizedLogin:
                mind.broker.transport.loseConnection('Unauthorized login.')
            else:
                mind.broker.transport.loseConnection('Could not login.')
            return failure
        d.addErrback(failed_login)
        return d


class Server:
    def __init__(self):
        self.realm.server = self

    def listen(self, address):
        self.host, self.port = utils.parse_host_port(address, 8800)

        try:
            reactor.listenTCP(self.port, self.factory, interface=self.host)
        except error.CannotListenError, e:
            logger.error(e)
            # wraps the error in a slightly more generic ServerError
            ## and reraises
            raise ServerError(str(e))

        # add the realm to each checker for later reference
        for checker in self.checkers:
            checker.realm = self.realm

        self.now_listening()

    def listenSSL(self, address, key_path, cert_path, cert_chain_path=None):
        self.host, self.port = utils.parse_host_port(address, 2220)

        # verify that the given key/cert files actually exist
        if not os.path.exists(key_path):
            raise ServerError('Key file %r does not exist!' % key_path)
        if not os.path.exists(cert_path):
            raise ServerError('Cert file %r does not exist!' % cert_path)
        if cert_chain_path and not os.path.exists(cert_chain_path):
            raise ServerError('Cert chain file %r does not exist!' % \
                cert_chain_path)

        #ctx = ssl.DefaultOpenSSLContextFactory.getContext(self)
        self.contextFactory = ssl.DefaultOpenSSLContextFactory(key_path, cert_path)
        if cert_chain_path:
            self.contextFactory._context.use_certificate_chain_file(cert_chain_path)
        #ctx.set_verify(
        #    SSL.VERIFY_PEER | SSL.VERIFY_FAIL_IF_NO_PEER_CERT
        #)
        #ctx.load_verify_locations(cert_chain_path)
                                                                                                                                        
        try:
            reactor.listenSSL(self.port, self.factory, self.contextFactory,
                interface=self.host)
        except error.CannotListenError, e:
            logger.error(e)
            # wraps the error in a slightly more generic ServerError
            ## and reraises
            raise ServerError(str(e))

        # add the realm to each checker for later reference
        for checker in self.checkers:
            checker.realm = self.realm

        self.now_listening_ssl()

    def manhole(self, address, namespace={}, checker=None,
            manholeObject=None, **users):
        """
        Start an SSH manhole at the given address, validating against the
        users in the given dict.

        The namespace will be updated with any methods on this class that
        start with manhole_, but will have the prefix stripped.

        The manholeObject can be given, to allow code separation for manhole
        methods.
        """
        if not manholeObject:
            manholeObject = self

        self.manhole_host, self.manhole_port = \
            utils.parse_host_port(address, 2222)

        from twisted.conch.manhole import ColoredManhole
        from twisted.conch.manhole_ssh import ConchFactory, TerminalRealm
        from twisted.cred import portal, checkers

        def getManhole(_):
            manhole_objs = [getattr(manholeObject, n) \
                for n in dir(manholeObject) if n.startswith('manhole_')]
            namespace.update({f.func_name.lstrip('manhole_'): \
                f for f in manhole_objs if callable(f)})

            return ColoredManhole(namespace)

        realm = TerminalRealm()
        realm.chainedProtocolFactory.protocolFactory = getManhole
        p = portal.Portal(realm)
        if checker:
            p.registerChecker(checker)
        else:
            logger.warning('Highly insecure checker used for SSH manhole!')
            p.registerChecker(
                checkers.InMemoryUsernamePasswordDatabaseDontUse(**users))
        manholeObject.manhole_factory = ConchFactory(p)

        try:
            reactor.listenTCP(self.manhole_port,
                manholeObject.manhole_factory,
                interface=self.manhole_host)
        except error.CannotListenError, e:
            logger.error(e)
            # wraps the error in a slightly more generic ServerError
            ## and reraises
            raise ServerError(str(e))

        self.now_listening_manhole()

    def now_listening(self):
        logger.info('Listening for connections at %s:%d' % (
            self.host, self.port))

    def now_listening_ssl(self):
        logger.info('Listening for SSL connections at %s:%d' % (
            self.host, self.port))

    def now_listening_manhole(self):
        logger.info('Manhole listening at %s:%d' % (
            self.manhole_host, self.manhole_port))

    @property
    def factory(self):
        try:
            return self.__factory
        except AttributeError:
            self.__factory = ServerFactory(self.portal)
            return self.__factory

    @property
    def realm(self):
        try:
            return self.__realm
        except AttributeError:
            self.__realm = Realm()
            return self.__realm

    @property
    def portal(self):
        try:
            return self.__portal
        except AttributeError:
            p = Portal(self.realm, checkers=self.checkers)
            self.realm.portal = p
            self.__portal = p
            return self.__portal

    @property
    def checkers(self):
        """
        Return a list of checker instances.

        See the Twisted documentation for more information:
            http://twistedmatrix.com/documents/current/api/twisted.cred.checkers.html
        """
        raise NotImplementedError('No checkers supplied for server '
            'at %s.' % self.realm)

class Realm:
    implements(portal.IRealm)

    def __init__(self, name='Realm'):
        self.avatars = {}
        self.name = name
        self.user = User

    def __str__(self):
        """
        Displays the string representation of an instance.

        Set a name attribute on the realm to customize.
        """
        return getattr(self, 'name', 'Default Realm')

    def requestAvatar(self, avatarID, mind, *interfaces):
        """
        Provides an avatar instance to the Portal.
        """
        assert pb.IPerspective in interfaces
        avatar_list = self.avatars.get(avatarID, [])
        avatar = self.user(avatarID)
        avatar.realm = self
        avatar.server = self.server
        avatar_list.append(avatar)
        self.avatars[avatarID] = avatar_list
        avatar.connected(mind)
        def disconnected():
            avatar_list = self.avatars.get(avatarID, [])
            for a in avatar_list[:]:
                if a == avatar:
                    avatar_list.remove(a)
                    a.disconnected(mind)
        return pb.IPerspective, avatar, lambda: disconnected()


class UserError(Exception):
    pass


class User(BaseAvatar):
    def __init__(self, *args, **kwargs):
        BaseAvatar.__init__(self, *args, **kwargs)
        self.permissions = []

    def has_permissions(self, permissions_list):
        """
        Returns a deferred which fires with a subset list of permissions
        from the given permissions_list that the user actually has,
        according to the checkers on the portal that the user logged in
        via.
        """
        d = defer.Deferred()
        # parse permissions recv'd from the checkers (and the DeferredList)
        def got_permissions(results):
            permissions = []
            for perms in [result for success, result in results if success]:
                for perm in perms:
                    if perm not in permissions:
                        permissions.append(perm)
            # begin callback chain on the deferred that we returned when
            ## has_permissions was originally called, passing the list of
            ## valid permissions recv'd from the checkers
            d.callback(permissions)
        # if an error happened, then return an empty set
        def error(failure):
            d.callback([])
        # ask checkers for the permissions for this user
        ## (using set here makes the list of checkers unique)
        dl = []
        for checker in set(self.realm.portal.checkers.values()):
            try:
                dl.append(checker.requestPermissions(self.username,
                    permissions_list))
            except AttributeError:
                pass
        defer.DeferredList(dl).addCallback(got_permissions).addErrback(error)
        return d

    def message(self, text):
        """
        Send a text message to this user.
        """
        if not self.is_connected():
            raise UserError('User is not connected.')
        self.callRemote('message', text)
