import logging
import string
from urllib import unquote

# create a log target for this module
logger = logging.getLogger(__name__)

def value_cleanup(value):
    # remove url formatting from the value
    value = unquote(value)
    return value


class EventDict(dict):
    """
    Parses a given string containing key: value pairs delimited by linefeeds
    into a dictionary. Additionally, the attributes content_length and 
    content_type will be added and set to the value of the Content-Length and
    Content-Type keys, or default values if those keys are not present.
    """
    def __init__(self, data):
        self.raw = data
        self.content = None
        # some event data contains a content block within it
        if data.find('\n\n') != -1:
            data, self.content = data.split('\n\n', 1)
        try:
            for key, value in [
                    pair.split(':', 1) for pair in data.split('\n') if pair]:
                self[key.strip()] = value_cleanup(value.lstrip())
        except ValueError, e:
            logger.error('Unable to parse data: %r' % data)
            raise e
        self.content_type = self.get('Content-Type', '').strip()
        self.content_length = int(self.get('Content-Length', 0))
        if self.content and len(self.content) != self.content_length:
            logger.warning('Content-Length value does not match the actual '
                'content length.')


def eventname2funcname(eventname, subclass=''):
    funcname = 'on' + eventname.title().replace('_', '')
    if subclass:
        funcname = '_'.join([funcname, subclass.title().replace('::', '')])
    return funcname

def funcname2eventname(funcname):
    try:
        eventname, subclass = funcname.split('_', 1)
    except ValueError:
        eventname, subclass = funcname, ''
    if not eventname.startswith('on'):
        raise ValueError("Unable to discern the event name.")
    eventname = eventname[2:]
    for letter in string.uppercase:
        if letter not in eventname[1:]:
            continue
        eventname = eventname[0] + eventname[1:].replace(letter, '_' + letter)
    if subclass:
        for letter in string.uppercase:
            if letter not in subclass[1:]:
                continue
            subclass = subclass[0] + subclass[1:].replace(letter, '::' + letter)
    return (eventname.upper(), subclass.lower())

def format_event(event_title, event_dict, content=None):
    """
    Returns a string representation of the event information,
    formatted in a manner suitable for humans to inspect the event
    data manually. Especially useful for debugging purposes.
    """
    # create a sorted list of event keys
    keys = event_dict.keys()
    keys.sort()
    event_text = '\n'.join(
        ['%30s: %s' % (key, event_dict.get(key)) for key in keys])
    if content:
        event_text = '%s\n\n%s' % (event_text, content)
    return '%(topline)s\n%(event_text)s\n%(botline)s' % {
            'topline': event_title.center(80, '-'),
            'event_text': event_text,
            'botline': '=' * 80,
    }
