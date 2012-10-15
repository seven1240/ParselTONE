from collections import OrderedDict
import logging
from twisted.internet import defer
from parseltone.eventsocket import utils


# create a log target for this module
logger = logging.getLogger(__name__)


class Event(object):
    subscription_funcname = None
    successful = True

    def __init__(self, protocol, event_dict, content):
        self.protocol = protocol
        self.deferred = defer.Deferred()
        self.type = event_dict.content_type
        self.dict = event_dict
        self.content = content
        # do custom event parsing
        self.parse()
        if protocol.verboseEvents:
            logger.debug('Event received:\n' + self.render())

    def __str__(self):
        return self.type

    def parse(self):
        """
        Override to provide custom event parsing.
        """
        pass

    def render(self):
        """
        Returns a string representation of the event, primarily for 
        debugging purposes.
        """
        return utils.format_event(str(self), self.dict, content=self.content)

    def response(self):
        """
        If a response is given here, then the deferred will be called when
        the corresponding command/reply is received from FreeSWITCH.
        """
        return None

    def finish(self):
        """
        If the protocol has a deferred waiting, this method will trigger it
        with the event. If the successful attribute on this event instance 
        returns True, the deferred callback chain will be triggered, otherwise
        the errback chain will.
        """
        if self.protocol._deferred:
            self.deferred = self.protocol._deferred
            self.protocol._deferred = None
            if self.successful:
                self.deferred.callback(self)
            else:
                self.deferred.errback(self)


class AuthRequestEvent(Event):
    def response(self):
        def error(message):
            logger.error(message)
        self.deferred.addCallback(self.protocol.authSuccess)
        self.deferred.addErrback(error)
        return 'auth $password'


class CommandReplyEvent(Event):
    def __str__(self):
        try:
            command = self.deferred.command
        except AttributeError:
            command = None
        try:
            command = ' '.join((command,) + self.deferred.args)
        except AttributeError:
            pass
        if command:
            return '{type} {command}'.format(
                type=self.type, command=repr(command))
        return self.type

    def parse(self):
        self.finish()

    @property
    def result(self):
        return self.dict['Reply-Text']

    @property
    def successful(self):
        return not bool(self.result.startswith('-ERR'))


class ApiResponseEvent(CommandReplyEvent):
    @property
    def result(self):
        return self.content


class PlainTextEvent(Event):
    def __str__(self):
        template = '{type} {name}'
        if self.subclass:
            if self.info:
                template = '{type} {name} {subclass} {info}'
            else:
                template = '{type} {name} {subclass}'
        elif self.info:
            template = '{type} {name} {info}'
        return template.format(type=self.type, name=self.name, 
            info=self.info, subclass=self.subclass)

    def parse(self):
        # content contains key:value pairs for plain text events
        content_dict = utils.EventDict(self.content)
        self.dict.update(content_dict)
        self.dict = OrderedDict(sorted(self.dict.items(), 
                                       key=lambda t: t[0].lower()))
        self.content = content_dict.content
        # delegate the event to any subscription functions
        self.delegate()

    def delegate(self):
        self.protocol._eventPlainTextDelegator(self, self.name, 
            subclass=self.subclass, content=self.content)

    @property
    def name(self):
        return self.dict.get('Event-Name', '').strip()

    @property
    def info(self):
        return self.dict.get('Event-Info', '').strip()

    @property
    def subclass(self):
        return self.dict.get('Event-Subclass', '').strip()

