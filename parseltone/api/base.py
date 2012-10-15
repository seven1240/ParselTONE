from parseltone.api.channel import Channel
from parseltone.api.commands import Commands


class Channels(dict):
    def active(self):
        """
        Returns a new dictionary populated only with channels that DO 
        currently exist in FreeSWITCH.
        """
        results = {}
        for uuid, channel in self.items():
            if not channel.exists():
                continue
            results.update({uuid: channel})
        return results

    def inactive(self):
        """
        Returns a new dictionary populated only with channels that DO NOT 
        currently exist in FreeSWITCH. (These channels existed at one time,
        but are now not connected.)
        """
        results = {}
        for uuid, channel in self.items():
            if channel.exists():
                continue
            results.update({uuid: channel})
        return results


class Subsystem(Commands):
    channels = Channels()

    def subscribe(self, target):
        """
        Allow target objects to subscribe directly through the subsystem.
        """
        self.eventsocket.subscribe(target)

    def flush(self, channel):
        """
        Stop internally tracking the given channel. Does not hang up the 
        channel.
        """
        self.channels.pop(channel.uuid)

    def onChannelOriginate(self, event, content):
        # TODO: create a channel object here, and add to channels dict
        pass

