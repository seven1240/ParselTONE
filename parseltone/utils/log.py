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
import logging
import logging.handlers
import os
import sys
try:
    from twisted.python import log as twisted_log
except ImportError:
    twisted_log = None


ENABLE_TWISTED_LOGGING = False
DATEFORMAT = '%d/%b/%Y %H:%M:%S'
LINESEP = os.linesep
INDENT = ' ' * 32
DEFAULT_LEVEL = logging.DEBUG


# Python 2.7+ has the NullHandler class builtin
try:
    NullHandler = logging.NullHandler
except AttributeError:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass


class SingleLevelStreamHandler(logging.StreamHandler):
    censored = False

    def emit(self, record):
        if not self.censored and self.level == record.levelno:
            logging.StreamHandler.emit(self, record)

class SysLogHandler(logging.handlers.SysLogHandler):
    censored = True
    name = 'Unconfigured'

    def emit(self, record):
        if not self.censored:
            logging.handlers.SysLogHandler.emit(self, record)

    def applyFormat(self):
        self.setFormatter(logging.Formatter(
            ' '.join([self.name, '%(levelname)8s', '- %(message)s']),
            DATEFORMAT))

# set logger to the lowest level possible, initially
logger = logging.getLogger('')
logger.setLevel(logging.NOTSET)

# add null handlers for all levels
null = NullHandler()
null.setLevel(logging.NOTSET)
logger.addHandler(null)

# assign a single level handler for each level
handlers = {
    logging.DEBUG: SingleLevelStreamHandler(),
    logging.INFO: SingleLevelStreamHandler(),
    logging.WARNING: SingleLevelStreamHandler(),
    logging.ERROR: SingleLevelStreamHandler(),
    logging.CRITICAL: SingleLevelStreamHandler(),
}
if os.name == 'posix':
    handlers.update({
        1000: SysLogHandler('/dev/log'),
    })

def configure_syslog_handler(name, censored):
    if os.name != 'posix':
        return
    handlers[1000].name = name
    handlers[1000].censored = censored
    handlers[1000].applyFormat()

def get_formatter(level):
    # default to DEBUG if the level is invalid
    if level not in handlers.keys():
        level = logging.DEBUG
    # return the appropriate formatter
    if level == logging.DEBUG:
        return logging.Formatter(
            ' '.join(['[%(asctime)s]', '%(levelname)8s', '- (%(name)s)',
            '%(funcName)s :%(lineno)d', LINESEP, INDENT, '%(message)s']),
            DATEFORMAT)
    return logging.Formatter(
        ' '.join(['[%(asctime)s]', '%(levelname)8s', '- %(message)s']),
        DATEFORMAT)

def configure_handlers(level):
    """
    Configure (and install) handlers appropriate for the level.
    """
    logging.info('Logging %s messages and higher.' % \
        logging.getLevelName(level))

    for hlevel in handlers.keys():
        # avoid duplicate handlers by removing the handler first
        logger.removeHandler(handlers.get(hlevel))
        if hlevel < level:
            logger.addHandler(null)
            continue
        handlers[hlevel].setLevel(hlevel)
        handlers[hlevel].setFormatter(get_formatter(hlevel))
        logger.addHandler(handlers.get(hlevel))

    # default to censoring the syslog handler
    if os.name == 'posix':
        syslog = handlers[1000]
        syslog.setLevel(logging.DEBUG)
        syslog.applyFormat()
        logger.addHandler(syslog)

def censor_stream_handlers():
    for handler in handlers.values():
        handler.censored = True

def uncensor_stream_handlers():
    for handler in handlers.values():
        handler.censored = False

# configure handlers for the default level initially
configure_handlers(DEFAULT_LEVEL)

if ENABLE_TWISTED_LOGGING and twisted_log:
    # start twisted logging
    twisted_log.startLogging(sys.stdout)

    # twisted logging observer
    observer = twisted_log.PythonLoggingObserver()
    observer.start()

## log everything, sending it to stderr
#logging.basicConfig(level=logging.DEBUG)
