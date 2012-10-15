import base64
import logging
import string
import urllib
import urlparse
from twisted.cred import checkers, credentials, error
from twisted.internet import defer
from twisted.python import failure
from twisted.web.client import getPage
from zope.interface import implements


# create a log target for this module
logger = logging.getLogger(__name__)


TRUE_VALUES = [True, 'true', 'yes']
FALSE_VALUES = [False, 'false', 'no']


def value_conversion(value):
    if len(value) == 1:
        value = value[0]
    if value.lower() in TRUE_VALUES:
        return True
    if value.lower() in FALSE_VALUES:
        return True
    return value


class UrlPostChecker:
    implements(checkers.ICredentialsChecker)
    credentialInterfaces = (credentials.IUsernamePassword,
        credentials.IUsernameHashedPassword)

    def __init__(self, base_url, verify_immediately=True, 
            test_permissions=False):
        r = urlparse.urlsplit(base_url)
        self.scheme, self.host, self.port = r.scheme, r.hostname, r.port
        self.path, self.query, self.fragment = r.path, r.query, r.fragment
        self.test_permissions = test_permissions
        if not self.path.endswith('/'):
            self.path = self.path + '/'
        if verify_immediately:
            self.verify_urls()

    def verify_urls(self):
        """
        Tests both the login URL and the permissions URL, and warns
        if either is not working at the moment. These warnings are 
        for troubleshooting purposes, and are not considered errors;
        the web service could very well be responding by the time a 
        client requests authentication later.
        """
        logger.debug('Verifying login and permissions URLs..')

        headers = {}
        basicAuth = self.basic_auth(verifying=True)
        if basicAuth:
            headers.update({'Authorization': basicAuth})

        # test login URL
        def login_page_down(failure):
            logger.warning('The url at %r is not currently '
                'responding.' % self.login_url)
            logger.warning('Client authentication might not function properly.')
        d = getPage(self.login_url, method='POST', headers=headers or None,
            postdata=urllib.urlencode({'check': True}))
        d.addErrback(login_page_down)

        # test permissions URL
        if self.test_permissions:
            def permissions_page_down(failure):
                logger.warning('The url at %r is not currently '
                    'responding.' % self.permissions_url)
                logger.warning('Determining permissions for clients might not '
                    'function properly.')
            d = getPage(self.permissions_url, method='POST',
                postdata=urllib.urlencode({'check': True}))
            d.addErrback(permissions_page_down)

    @property
    def base_url(self):
        netloc = self.host
        if self.port:
            netloc = ':'.join([self.host, str(self.port)])
        return urlparse.urlunsplit((self.scheme, netloc, self.path, 
            self.query, self.fragment))

    @property
    def login_url(self):
        return self.base_url

    @property
    def permissions_url(self):
        return urlparse.urljoin(self.base_url, 'permissions/')

    def basic_auth(self, verifying=False):
        if verifying:
            # don't use basic auth when verifying urls
            return None
        username = getattr(self, 'username', None)
        password = getattr(self, 'password', None)
        if not (username and password):
            # don't use basic auth without both username and password
            return None
        return 'Basic ' + base64.encodestring(
            ':'.join([username, password])).strip()

    def login_post_dict(self, credential):
        try:
            password = credential.password
        except AttributeError:
            # IUsernameHashedPassword credentials have no password, but
            # a response instead
            password = credential.response
        return {'username': credential.username, 'password': password}

    def permissions_post_dict(self, username, permissions):
        # transmit permissions as a string in CSV format
        permissions = ', '.join(permissions)
        return {'username': username, 'permissions': permissions}

    def _HttpFailure(self, failure):
        try:
            logger.error('(%s: %s) %s', failure.value.status,
                failure.value.message, failure.value.response)
        except AttributeError:
            logger.error(failure.getErrorMessage())

    def parse_data(self, data):
        """
        Pass in a url-encoded string of data.

        Returns a dictionary of key:value pairs, with values
        slightly cleaned up.
        """
        # parse out the query string in the data
        data = urlparse.parse_qs(data, True)

        # clean up the parsed data, since the dictionary can look
        ## something like {'foo': 'True', 'bar': 'False'}
        for key, value in data.items():
            data[key] = value_conversion(value)

        return data

    def got_credential_result(self, data, credential):
        """
        Data should contain a 'success' key.
        """
        # parse out the query string in the data
        data = self.parse_data(data)

        # actually check the data for the values we want!
        access = data.get('success', False)
        if access:
            logger.debug('User %r granted access to %r.' % (
                credential.username, self.realm.name))
        else:
            logger.debug('User %r denied access to %r.' % (
                credential.username, self.realm.name))
        return access

    def _checkCredential(self, credential):
        headers = {}
        basicAuth = self.basic_auth()
        if basicAuth:
            headers.update({'Authorization': basicAuth})

        d = getPage(self.login_url, method='POST', headers=headers or None,
            postdata=urllib.urlencode(self.login_post_dict(credential)))
        d.addCallback(self.got_credential_result, credential).addErrback(
            self._HttpFailure)
        return d

    def _cbCredential(self, matched, credential):
        if matched:
            return credential.username
        else:
            return failure.Failure(error.UnauthorizedLogin())

    def requestAvatarId(self, credential):
        return defer.maybeDeferred(self._checkCredential,
            credential).addCallback(self._cbCredential, credential)

    def got_permissions_result(self, data):
        """
        Data should contain a 'permissions' key.
        """
        # parse out the query string in the data
        data = self.parse_data(data)

        # actually check the data for the values we want!
        perms = data.get('permissions', '').split(',')
        # trim out any blank permissions values
        perms = [y for y in [x.strip() for x in perms] if y]
        return perms

    def requestPermissions(self, *args):
        """
        Returns a deferred which triggers with a valid subset from the
        given list of permission names for the username.
        """
        headers = {}
        basicAuth = self.basic_auth()
        if basicAuth:
            headers.update({'Authorization': basicAuth})

        d = getPage(self.permissions_url, method='POST', 
            headers=headers or None,
            postdata=urllib.urlencode(self.permissions_post_dict(*args)))
        d.addCallback(got_permissions_result).addErrback(self._HttpFailure)
        return d

