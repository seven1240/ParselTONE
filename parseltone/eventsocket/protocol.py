import logging
import string
from twisted.internet import defer
from twisted.protocols import basic
from parseltone.eventsocket import events, utils


# create a log target for this module
logger = logging.getLogger(__name__)


class EventError(Exception):
    pass


class RawEventSocket(basic.LineReceiver):
    delimiter = '\n\n'
    password = 'ClueCon'
    _event_dict = None
    _content = ''

    def connectionMade(self):
        self.setLineMode()

    def lineReceived(self, line):
            event_dict = utils.EventDict(line)
            # more content may be expected
            if event_dict.content_length:
                # preserve the event so that we can use it after receiving
                ## the expected content
                self._event_dict = event_dict
                # tell twisted that we want to receive raw data for our
                ## content
                self.setRawMode()
                return
            # event did not specify that it included any content, so it
            ## is complete
            self.eventReceived(event_dict)

    def rawDataReceived(self, data):
            # retrieve the event information
            event_dict = self._event_dict
            # append data to the content
            self._content += data
            # if not finished receiving content data yet, just return
            if len(self._content) < event_dict.content_length:
                return
            # we have complete content
            content = self._content
            # reset the class attributes to defaults
            self._content = ''
            self._event_dict = None
            # if the content length is too long, trim the extra, and pass
            ## it back to twisted when setting the linemode
            extra = ''
            if len(content) > event_dict.content_length:
                extra = content[event_dict.content_length:]
                content = content[:event_dict.content_length]
            # switch back to linemode, passing in any extra data received
            self.setLineMode(extra=extra)
            self.eventReceived(event_dict, content=content)

    def eventReceived(self, event_dict, content=None):
        raise NotImplementedError('eventReceived method must be implemented '
            'by %r subclass.' % self.__class__.__name__)


class BasicEventSocket(RawEventSocket):
    debug = False
    verboseEvents = False
    _deferred = None

    def __init__(self):
        self.event_handlers = {
            'auth/request': self._eventAuthRequest,
            'command/reply': self._eventCommandReply,
            'text/event-plain': self._eventPlainText,
            'api/response': self._eventApiResponse,
        }

    def eventReceived(self, event_dict, content=None):
        # find the event handler, and warn if one doesn't exist for this event
        event_handler = self.event_handlers.get(event_dict.content_type, None)
        if not event_handler:
            logger.warning('Support for event type %r is '
                'not implemented.' % event_dict.content_type)
            return
        # pass to event handler
        event_handler(event_dict, content)

    def authSuccess(self, response):
        pass

    def authFailure(self, failure):
        logger.error(failure.getErrorMessage())

    def _eventAuthRequest(self, event_dict, content):
        # render to logs, if enabled
        if self.verboseEvents:
            logger.info('Event received:\n%s' % utils.format_event(
                event_dict.content_type, event_dict, content=content))
        # construct a deferred object to use when we receive the
        ## command/reply event in response to the sendLine below
        self._deferred = defer.Deferred()
        self._deferred.command = 'auth'
        self._deferred.addCallback(self.authSuccess).addErrback(
            self.authFailure)
        # send the auth command
        self.sendLine('auth {password}'.format(password=self.password))

    def _eventCommandReply(self, event_dict, content):
        # render to logs, if enabled
        if self.verboseEvents:
            title = event_dict.content_type
            if hasattr(self._deferred, 'command'):
                command = self._deferred.command
                if hasattr(self._deferred, 'args'):
                    command = ' '.join((command,) + self._deferred.args)
                title = ' '.join([title, repr(command)])
            logger.info('Event received:\n%s' % utils.format_event(
                title, event_dict, content=content))
        # determine how to handle the result
        result = event_dict['Reply-Text']
        if result.startswith('-ERR'):
            if self._deferred:
                self._deferred.errback(result)
                self._deferred = None
                return
            raise EventError(result)
        if self._deferred:
            self._deferred.callback(result)
            self._deferred = None
            return
        logger.info(result)

    def _eventApiResponse(self, event_dict, content):
        # render to logs, if enabled
        if self.verboseEvents:
            title = event_dict.content_type
            if hasattr(self._deferred, 'command'):
                command = self._deferred.command
                if hasattr(self._deferred, 'args'):
                    command = ' '.join((command,) + self._deferred.args)
                title = ' '.join([title, repr(command)])
            logger.info('Event received:\n%s' % utils.format_event(
                title, event_dict, content=content))
        # determine how to handle the result
        if content.startswith('-ERR'):
            if self._deferred:
                self._deferred.errback(content)
                self._deferred = None
                return
            raise EventError(content)
        if self._deferred:
            self._deferred.callback(content)
            self._deferred = None
            return
        logger.info(content)

    def _eventPlainText(self, event_dict, content):
        # parse the content into a dictionary of key:value pairs, along with
        ## any content block it may contain as the internal_content attribute
        ## on the content_dict object
        content_dict = utils.EventDict(content)
        # update the event dict with the key:value pairs from the content_dict
        event_dict.update(content_dict)
        # set some useful local variables
        event_name = event_dict.get('Event-Name', '').strip()
        event_subclass = event_dict.get('Event-Subclass', '').strip()
        # render to logs, if enabled
        if self.verboseEvents:
            title = event_dict.content_type
            if event_name:
                title = ' '.join([title, event_name])
            if event_subclass:
                title = ' '.join([title, event_subclass])
            logger.info('Event received:\n%s' % utils.format_event(
                title, event_dict, content=content_dict.content))
        # delegate the event to subscription functions
        self._eventPlainTextDelegator(event_dict, event_name,
            subclass=event_subclass, content=content_dict.content)

    def _eventPlainTextDelegator(self, obj, name, subclass=None, content=None):
        # determine the subscription function name
        funcname = utils.eventname2funcname(name, subclass=subclass)
        # get the function, if it exists
        subscription_func = getattr(self, funcname, None)
        # construct an informative event title
        title = name
        if subclass:
            title = ' '.join([title, subclass])
        # if the function is not usable for any reason, log about it
        if not subscription_func:
            logger.error('Subscription function %r not defined for '
                'event %s.' % (funcname, title))
            return
        if not callable(subscription_func):
            logger.error('Subscription function %r for event %s is not '
                'callable.' % (funcname, title))
            return
        # invoke the subscription function
        subscription_func(obj, content)

    def api(self, command, *args):
        self._deferred = defer.Deferred()
        self._deferred.command = command
        self._deferred.args = args
        self.sendLine('api %s %s' % (command, ' '.join(args)))
        return self._deferred

    def bgapi(self, command, *args):
        self._deferred = defer.Deferred()
        self._deferred.command = command
        self._deferred.args = args
        self.sendLine('bgapi %s %s' % (command, ' '.join(args)))
        return self._deferred


class EventSocket(BasicEventSocket):
    response_substitutions = {}

    def __init__(self):
        self.authorized = False
        self.event_handlers = {
            'auth/request': events.AuthRequestEvent,
            'command/reply': events.CommandReplyEvent,
            'text/event-plain': events.PlainTextEvent,
            'api/response': events.ApiResponseEvent,
        }
        self.pending_jobs = {}
        # NOTE: always subscribe to BACKGROUND_JOB for bgapi responses
        self.event_subscriptions = {
            'BACKGROUND_JOB': [],
        }
        # this class is always a subscriber
        self.subscribe(self)

    def authSuccess(self, response):
        self.authorized = True
        self.registerSubscribedEvents()

    def registerSubscribedEvents(self):
        if not self.authorized:
            return
        # if any subscribers are interested in all events, we just need to
        ## register for all of them, and we're done
        if self.event_subscriptions.get('ALL', []):
            if self.debug:
                logger.debug('Registering for all events.')
            self.sendLine('event plain all')
            return
        eventlist = [e for e in self.event_subscriptions.keys() \
            if not e.startswith('CUSTOM')]
        customeventlist = [e.split()[-1] for e in \
            self.event_subscriptions.keys() if e.startswith('CUSTOM')]
        # append custom event subclasses to the end of the list
        if customeventlist:
            eventlist.append('CUSTOM')
            for c in customeventlist:
                eventlist.append(c)
        # register for the events with FreeSWITCH
        if self.debug:
            logger.debug('Registering for event(s): %s' % ' '.join(eventlist))
        self.sendLine('event plain %s' % ' '.join(eventlist))

    def eventReceived(self, event_dict, content=None):
        # pass to event handler
        event_handler = self.event_handlers.get(event_dict.content_type,
            events.Event)
        event = event_handler(self, event_dict, content)
        if event_handler == events.Event:
            logger.warning('Support for event type %r is '
                'not implemented.' % event_dict.content_type)
        # if there is a response given for this event, then send it over the
        ## wire to the distant end
        response = event.response()
        if response:
            # set the deferred to callback when command/reply is recv'd
            self._deferred = event.deferred
            # provide support for specific substitutions in the response
            response = string.Template(response).safe_substitute(
                self.response_substitutions)
            if self.debug:
                logger.debug('TX: %r', response)
            # in order to avoid accidentally exposing the password outside
            ## of the code, add it only after logging is done, and deferred
            ## command info is set
            self._deferred.command = response
            response = string.Template(response).safe_substitute(
                {'password': self.password})
            # send response to distant end
            self.sendLine(str(response))

    def subscribe(self, obj):
        """
        Subscribe obj to receive events.
        """
        # function to append subscribers to the proper list
        def append_event(eventname, subclass, subscriber):
            eventkey = eventname
            # custom events will have a subclass
            if subclass:
                eventkey = ' '.join([eventname, subclass])
            subscribers = self.event_subscriptions.get(eventkey, [])
            if subscriber not in subscribers:
                subscribers.append(subscriber)
            self.event_subscriptions[eventkey] = subscribers
        # find functions that meet a specific naming convention, denoting
        ## that they are subscribing to an event, then determine which
        ## event they are subscribing to
        for funcname in dir(obj):
            if not funcname.startswith('on'):
                continue
            if not callable(getattr(obj, funcname, None)):
                continue
            eventname, subclass = utils.funcname2eventname(funcname)
            append_event(eventname, subclass, getattr(obj, funcname, None))
        self.registerSubscribedEvents()

    def _eventPlainTextDelegator(self, event, name, subclass=None, content=None):
        # watch for background job events and provide additional handling for
        ## the pending_jobs deferred objects waiting for bgapi response data
        if name == 'BACKGROUND_JOB':
            job_deferred = self.pending_jobs.get(event.dict['Job-UUID'], None)
            if job_deferred:
                job_deferred.callback(content)
        # determine the subscription function name
        funcname = utils.eventname2funcname(name, subclass=subclass)
        # construct the function list from all subscribers
        # NOTE: we copy the retrieved list into a new list object, to
        ## avoid object reference issues causing the list contained in
        ## the event_subscriptions dict to be modified
        if subclass:
            funclist = list(self.event_subscriptions.get(
                ' '.join([name, subclass]), []))
        else:
            funclist = list(self.event_subscriptions.get(name, []))
        # make sure subscribers for ALL events get this one
        funclist += self.event_subscriptions.get('ALL', [])
        # construct an informative event title
        title = name
        if subclass:
            title = ' '.join([title, subclass])
        for func in funclist:
            if not callable(func):
                logger.error('Subscription function %r for event %s is '
                    'not callable.' % (funcname, title))
                continue
            # invoke the subscription function
            func(event, content)

    def api(self, command, *args):
        # TODO: see the todo for bgapi below; calling api commands back-to-back
        ## exhibits very similar behavior, and should be fixed with queueing as
        ## well.
        self._deferred = defer.Deferred()
        self._deferred.command = command
        self._deferred.args = args
        # create a deferred object to be triggered when the command has finished
        command_deferred = defer.Deferred()
        def success(event):
            # FreeSWITCH executed the command
            command_deferred.callback(event.result)
        def failure(error):
            # FreeSWITCH failed to execute the command, so we errback
            command_deferred.errback(error)
        self._deferred.addCallback(success).addErrback(failure)
        self.sendLine('api %s %s' % (command, ' '.join(args)))
        # return the command_deferred object, so the user can add callbacks
        return command_deferred

    def bgapi(self, command, *args):
        # TODO: calling multiple bgapi (or api) commands back-to-back
        ## will break the deferred callback flow here, by reassigning
        ## the self._deferred attribute to a new Deferred object, losing
        ## the previous object. This means that the Job-UUID response
        ## event for the previous bgapi call will end up being assigned
        ## to the later bgapi call, and subsequent job response for that
        ## Job-UUID will go to the later bgapi calls deferred object.
        ## This needs to be fixed at a later time with some sort of bgapi
        ## queueing, but for now can be worked around by chaining bgapi
        ## calls through with deferred callbacks.

        # create the default deferred object, for determining whether
        ## FreeSWITCH successfully started the background job
        self._deferred = defer.Deferred()
        self._deferred.command = command
        self._deferred.args = args
        # create a deferred object to be triggered when the job has finished
        job_deferred = defer.Deferred()
        def success(event):
            # FreeSWITCH started the background job, so we want to update
            ## the pending_jobs dictionary with our job_deferred object,
            ## keyed by the job id that FreeSWITCH assigned
            self.pending_jobs.update({event.dict['Job-UUID']: job_deferred})
        def failure(error):
            # FreeSWITCH failed to start the background job, so we errback
            job_deferred.errback(error)
        self._deferred.addCallback(success).addErrback(failure)
        self.sendLine(str('bgapi %s %s' % (command, ' '.join(args))))
        # return the job_deferred object, so the user can add callbacks
        return job_deferred
