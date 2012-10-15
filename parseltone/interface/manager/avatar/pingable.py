import datetime
import logging
from twisted.internet import reactor

# create a log target for this module
logger = logging.getLogger(__name__)


class Pingable:
    def __init__(self, max_latency_secs=2):
        self.max_latency = max_latency_secs * 1000
        self.max_latency_secs = max_latency_secs
        # warning latency is 75% of the max
        self.warning_latency = self.max_latency * 0.75

    def connected(self):
        # start the ping train
        self.ping()

    def disconnected(self):
        try:
            del self.__latency_test_timer
        except AttributeError:
            pass
        try:
            del self.__latency_utcdt
        except AttributeError:
            pass

    def ping(self):
        if not self.is_connected():
            return
        now = datetime.datetime.utcnow()
        # if no prior ping response, set it to now; this means that
        ## the client probably only just connected, and this is the
        ## first ping to them, so we want to treat that connection
        ## as the last response we got from the client
        try:
            self.__latency_utcdt
        except AttributeError:
            self.__latency_utcdt = now

        def ping_response(utcdt):
            """
            Called when the ping response has been received from the client.
            This function will record the utcdt in the response, then cancel
            the latency disconnect timer, and start a new ping request.
            """
            if not self.is_connected():
                return
            if self.latency >= self.warning_latency:
                logger.warning("%(user)r has an uncomfortable amount of "
                    "latency: %(latency)dms" % {
                        'user': str(self),
                        'latency': self.latency,
                    })
            # don't use the clients utcdt, since their clock is probably
            ## out of sync with ours
            self.__latency_utcdt = datetime.datetime.utcnow()
            try:
                self.__latency_disconnect.cancel()
            except error.AlreadyCancelled:
                pass
            reactor.callLater(1, self.ping)

        def latency_disconnect():
            """
            Called when no ping response has been received for longer than
            the max_latency value. This means that the client needs to be
            forcibly disconnected.
            """
            # don't do anything if the client isn't connected
            if not self.is_connected():
                return
            # anal retentive double check, just in case this function was
            ## invoked during the wrong conditions
            if not self.latency >= self.max_latency:
                # call this again in cinco segundos
                try:
                    self.__latency_disconnect.reset(self.max_latency_secs)
                except AttributeError:
                    self.__latency_disconnect = reactor.callLater(
                        self.max_latency_secs, latency_disconnect)
            self.disconnect("%(user)r has exceeded max latency and will be "
                "forcibly disconnected: %(latency)dms" % {
                    'user': str(self),
                    'latency': self.latency,
                })

        # start the latency disconnect timer; this will be cancelled when we
        ## get a ping response from the client, or else it will trigger
        ## at max_latency and disconnect the client
        self.__latency_disconnect = reactor.callLater(self.max_latency_secs,
            latency_disconnect)
        # send the client a ping request, and set up the ping_response
        ## function to be called when they respond
        self.callRemote('ping', now).addCallback(ping_response)

    @property
    def latency(self):
        """
        Returns the current latency of this user in seconds, or -1 if unknown.
        """
        if not self.is_connected():
            raise UserError('User is not connected.')
        try:
            self.__latency_utcdt
        except AttributeError:
            return -1
        td = datetime.datetime.utcnow() - self.__latency_utcdt
        seconds = float(td.days) * 24 * 60 * 60 + td.seconds + (
            td.microseconds * 10**-6)
        latency = seconds * 1000
        return latency
