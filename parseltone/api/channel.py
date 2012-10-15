import logging
from twisted.internet import defer
from parseltone.utils.decorators import requires_attr

# create a log target for this module
logger = logging.getLogger(__name__)


# TODO: I don't really like the way this is done very much, but for now, 
## it accomplishes the goal of reducing repetitive code
def bgapi_wrapper(command, 
        success_func=lambda data: d.callback(data), 
        failure_func=lambda failure: logger.error(failure.getErrorMessage())):
    d = defer.Deferred()
    self.eventsocket.bgapi(command).addCallback(
        success_func).addErrback(failure_func)
    return d


class ChannelEvents(object):
    def __init__(self, channel, eventsocket):
        self.channel = channel
        self.eventsocket = eventsocket
        self.eventsocket.subscribe(self)


class Channel(object):
    _uuid_required_error = "Channel not established, method '{func}' invalid."

    def __init__(self, eventsocket, uuid=None):
        self.eventsocket = eventsocket
        self.eventlistener = ChannelEvents(self, eventsocket)
        self.uuid = uuid

    # TODO: create_uuid --- may not actually be useful, since we have 
    ## python's uuid module

    @requires_attr('uuid')
    def pause(self):
        """
        Pause media.
        """
        return bgapi_wrapper('pause {uuid} on'.format(uuid=self.uuid))

    @requires_attr('uuid')
    def resume(self):
        """
        Resume media.
        """
        return bgapi_wrapper('pause {uuid} off'.format(uuid=self.uuid))

    @requires_attr('uuid')
    def set_read_volume(self, level=0, mute=False):
        """
        Adjust the read audio levels on this channel.

        The level can be a value ranging from -4 (quiet) to 4 (loud), or 
        mute may be set. To restore normal volume, use the default level of 0, 
        with no mute.

        TODO: test if stopping the media bug here also stops any write bug.
        """
        if mute:
            return bgapi_wrapper('uuid_audio {uuid} start read mute'.format(
                uuid=self.uuid))
        elif level == 0:
            return bgapi_wrapper('uuid_audio {uuid} stop'.format(
                uuid=self.uuid))
        else:
            return bgapi_wrapper('uuid_audio {uuid} start read level '
                '{level}'.format(uuid=self.uuid, level=level))

    @requires_attr('uuid')
    def set_write_volume(self, level=0, mute=False):
        """
        Adjust the write audio levels on this channel.

        The level can be a value ranging from -4 (quiet) to 4 (loud), or 
        mute may be set. To restore normal volume, use the default level of 0, 
        with no mute.

        TODO: test if stopping the media bug here also stops any read bug.
        """
        if mute:
            return bgapi_wrapper('uuid_audio {uuid} start write mute'.format(
                uuid=self.uuid))
        elif level == 0:
            return bgapi_wrapper('uuid_audio {uuid} stop'.format(
                uuid=self.uuid))
        else:
            return bgapi_wrapper('uuid_audio {uuid} start write level '
                '{level}'.format(uuid=self.uuid, level=level))

    @requires_attr('uuid')
    def break_current(self):
        """
        Break out of media being sent to a channel. For example, if an audio 
        file is being played to a channel, issuing a break will discontinue 
        the CURRENTLY PLAYING media and the call will move on in the dialplan, 
        script, or whatever is controlling the call.
        """
        return bgapi_wrapper('uuid_break {uuid}'.format(uuid=self.uuid))

    @requires_attr('uuid')
    def break_all(self):
        """
        Break out of ALL media being sent to a channel. For example, if an 
        audio file is being played to a channel, issuing a break will 
        discontinue ALL QUEUED media and the call will move on in the dialplan, 
        script, or whatever is controlling the call.
        """
        return bgapi_wrapper('uuid_break {uuid} all'.format(uuid=self.uuid))

    @requires_attr('uuid')
    def bridge(self, to_uuid):
        """
        Bridges the channel to the to_uuid.
        """
        return bgapi_wrapper('uuid_bridge {uuid} {other_uuid}'.format(
            uuid=self.uuid, other_uuid=to_uuid))

    @requires_attr('uuid')
    def broadcast(self, app_name, *app_args):
        """
        Execute an arbitrary dialplan application on this channel.
        """
        app_with_args = '::'.join(app_args.insert(0, app_name))
        return bgapi_wrapper('uuid_broadcast {uuid} {app_with_args} aleg'.format(
            uuid=self.uuid,
            app_with_args=app_with_args,
        ))

    @requires_attr('uuid')
    def broadcast_file(self, filename):
        """
        Play a filename on this channel.
        """
        return bgapi_wrapper('uuid_broadcast {uuid} {filename} aleg'.format(
            uuid=self.uuid,
            filename=filename,
        ))

    @requires_attr('uuid')
    def buglist(self):
        """
        List the media bugs on this channel.
        """
        return bgapi_wrapper('uuid_buglist {uuid}'.format(uuid=self.uuid))

    @requires_attr('uuid')
    def chat(self, message):
        """
        If the endpoint has a receive_event handler, this sends a chat message.
        """
        return bgapi_wrapper('uuid_chat {uuid} {message}'.format(
            uuid=self.uuid,
            message=message,
        ))

    # TODO: uuid_debug_audio

    @requires_attr('uuid')
    def displace(self, filepath, limit=0, mux=False):
        """
        Plays limit seconds of the filepath to the channel, mixing transmitted
        audio if mux is True.
        """
        return bgapi_wrapper('uuid_displace {uuid} {filepath} {limit} '
            '{mux}'.format(
                uuid=self.uuid,
                filepath=filepath,
                limit=limit,
                mux='mux' if mux else '',
            ))

    @requires_attr('uuid')
    def display(self, text):
        """
        Updates the display if the endpoint supports this feature.
        """
        return bgapi_wrapper('uuid_display {uuid} {text}'.format(
            uuid=self.uuid, text=text))

    # TODO: uuid_dump -- may be redundant, depending on how we implement
    ## channel variable support

    @requires_attr('uuid')
    def exists(self):
        """
        Check whether this channel exists.
        """
        return bgapi_wrapper('uuid_exists {uuid}'.format(uuid=self.uuid))

    @requires_attr('uuid')
    def flush_dtmf(self):
        """
        Flush queued DTML digits.
        """
        return bgapi_wrapper('uuid_flush_dtml {uuid}'.format(uuid=self.uuid))

    # TODO: uuid_fileman

    @requires_attr('uuid')
    def getvar(self, varname):
        """
        Get a variable.

        TODO: Possibly redundant, depending on how we implement channel 
        variable support
        """
        return bgapi_wrapper('uuid_getvar {uuid} {varname}'.format(
            uuid=self.uuid, varname=varname))

    @requires_attr('uuid')
    def hold(self):
        """
        Place channel on hold.
        """
        return bgapi_wrapper('uuid_hold {uuid}'.format(uuid=self.uuid))

    @requires_attr('uuid')
    def unhold(self):
        """
        Take channel off hold.
        """
        return bgapi_wrapper('uuid_hold {uuid} off'.format(uuid=self.uuid))

    @requires_attr('uuid')
    def kill(self, cause=''):
        """
        Reset this channel.
        """
        return bgapi_wrapper('uuid_kill {uuid} {cause}'.format(
            uuid=self.uuid, cause=cause))

    # TODO: uuid_limit

    # TODO: uuid_media

    @requires_attr('uuid')
    def park(self):
        """
        Park this channel.
        """
        return bgapi_wrapper('uuid_park {uuid}'.format(uuid=self.uuid))

    # TODO: uuid_preprocess

    # TODO: uuid_recv_dtmf

    # TODO: uuid_send_dtmf

    # TODO: uuid_session_heartbeat

    @requires_attr('uuid')
    def setvar(self, varname, value):
        """
        Set a variable on the channel.
        """
        return bgapi_wrapper('uuid_setvar {uuid} {varname} {value}'.format(
            uuid=self.uuid, varname=varname, value=value))

    @requires_attr('uuid')
    def setvars(self, **data):
        """
        Set multiple variables on the channel.
        """
        return bgapi_wrapper('uuid_setvar_multi {uuid} {varstring}'.format(
            uuid=self.uuid,
            varstring=';'.join(['='.join([k, v]) for k, v in data.items()])
        ))

    @requires_attr('uuid')
    def simplify(self):
        """
        Directs FreeSWITCH to remove itself from the SIP signalling path 
        if possible.
        """
        return bgapi_wrapper('uuid_simplify {uuid}'.format(uuid=self.uuid))

    @requires_attr('uuid')
    def transfer(self, destination, dialplan='directory', context='default'):
        """
        Transfers this channel to a specific extension within the dialplan 
        and context. Dialplan may be 'xml' or 'directory'.
        """
        return bgapi_wrapper(
            'uuid_transfer {uuid} {destination} {dialplan} {context}'.format(
            uuid=self.uuid, 
            destination=destination, 
            dialplan=dialplan, 
            context=context,
        ))

    @requires_attr('uuid')
    def start_recording(self, path, limit=0):
        """
        Start recording the audio associated with this channel into the path 
        given. The format is dictated by the extension given in the path, if 
        available. If media setup has not happened yet for this channel, the 
        file will contain silent audio until media is available.
        """
        return bgapi_wrapper('uuid_record {uuid} start {path} {limit}'.format(
            uuid=self.uuid,
            path=path,
            limit=limit if limit else '',
        ))

    @requires_attr('uuid')
    def stop_recording(self, path):
        """
        Stop recording the audio associated with this channel into the path 
        given.
        """
        return bgapi_wrapper('uuid_record {uuid} stop {path}'.format(
            uuid=self.uuid,
            path=path,
        ))

    @requires_attr('uuid')
    def stop_all_recording(self):
        """
        Stop recording the audio associated with this channel into all files.
        """
        return bgapi_wrapper('uuid_record {uuid} stop {path}'.format(
            uuid=self.uuid,
            path=path,
        ))

    @requires_attr('uuid')
    def hangup(self, cause='', delay_secs=0):
        """
        Hangup this channel, after an optional delay.

        TODO: is this even useful? rather than using sched_hangup, just have 
        apps use reactor.callLater, and make this method call self.kill?
        """
        return bgapi_wrapper('sched_hangup +{delay} {uuid} {cause}'.format(
            uuid=self.uuid, delay=delay_secs, cause=cause))

    # TODO: tone_detect

