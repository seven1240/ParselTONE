import logging

logger = logging.getLogger(__name__)

def parse_host_port(hostname_string, default_port):
    try:
        host, port = hostname_string.split(':')
        try:
            port = int(port)
        except ValueError, e:
            logger.error('%r is not a valid port number.' % port)
            raise e
    except ValueError:
        host, port = hostname_string, default_port
    return str(host), int(port)
