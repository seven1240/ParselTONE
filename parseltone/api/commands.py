import logging
from twisted.internet import defer
from parseltone.api.channel import Channel

# create a log target for this module
logger = logging.getLogger(__name__)


class Commands(object):
    def __init__(self, eventsocket):
        self.eventsocket = eventsocket
        self.eventsocket.subscribe(self)

    def system(self, command):
        """
        Execute a command in the system shell on the FreeSWITCH machine.

        NOTE: This can lead to security bugs if you're not careful. For example,
        the following command is dangerous:

            system('log_caller_name $(caller_id_name)')

        If a malicious remote caller somehow sets their caller ID name to
        '; rm -rf /', you would unintentionally be executing this shell command:

            log_caller_name ; rm -rf /
        """
        command = 'system {command}'.format(command=command)
        d = defer.Deferred()
        def success(data):
            d.callback(data)
        def error(failure):
            logger.error(failure.getErrorMessage())
        self.eventsocket.bgapi(
            command).addCallback(success).addErrback(error)
        return d

    def get_user_attr(self, user, domain, attr):
        """
        Retrieve attribute from user at domain, as defined by the user directory.
        """
        command = 'user_data {user}@{domain} attr {attr}'.format(
            user=user, domain=domain, attr=attr)
        d = defer.Deferred()
        def success(data):
            d.callback(data)
        def error(failure):
            logger.error(failure.getErrorMessage())
        self.eventsocket.bgapi(
            command).addCallback(success).addErrback(error)
        return d
        

    def get_user_var(self, user, domain, var):
        """
        Retrieve variable from user at domain, as defined by the user directory.
        """
        command = 'user_data {user}@{domain} var {attr}'.format(
            user=user, domain=domain, var=var)
        d = defer.Deferred()
        def success(data):
            d.callback(data)
        def error(failure):
            logger.error(failure.getErrorMessage())
        self.eventsocket.bgapi(
            command).addCallback(success).addErrback(error)
        return d

    def get_user_param(self, user, domain, param):
        """
        Retrieve parameter from user at domain, as defined by the user directory.
        """
        command = 'user_data {user}@{domain} param {attr}'.format(
            user=user, domain=domain, param=param)
        d = defer.Deferred()
        def success(data):
            d.callback(data)
        def error(failure):
            logger.error(failure.getErrorMessage())
        self.eventsocket.bgapi(
            command).addCallback(success).addErrback(error)
        return d

    def does_user_exist(self, user, domain, key='id'):
        """
        Checks to see if a user exists; Matches user tags found in the directory.
        """
        command = 'user_exists {key} {user} {domain}'.format(
            key=key, user=user, domain=domain)
        d = defer.Deferred()
        def success(data):
            result = data.lower() == 'true'
            d.callback(result)
        def error(failure):
            logger.error(failure.getErrorMessage())
        self.eventsocket.bgapi(
            command).addCallback(success).addErrback(error)
        return d

    def originate_to_ext(self, destination, extension, 
            dialplan='', context='', timeout_sec=0,
            caller_id='Unknown', caller_id_number='0',
            local_vars={}, export_vars={}):
        """
        Originate a new call.

        TODO: document dialplan and context.
        """
        if timeout_sec and not (dialplan and context):
            raise ValueError('Both dialplan and context are required when a '
                'timeout_sec is specified.')
        if context and not dialplan:
            raise ValueError('Dialplan is required when a context '
                'is specified.')
        if local_vars or export_vars:
            if destination.startswith('{'):
                raise ValueError('Destination string already has channel '
                    'variables set. Can not add more.')
            # TODO: handle export_vars properly
            local_vars.update(export_vars)
            var_string = ','.join(
                ['='.join([k, v]) for k, v in local_vars.items()])
            destination = '{%s}%s' % (var_string, destination)
        command = 'originate {call_url} {exten} {dialplan} ' \
            '{context} {cid_name} {cid_num} {timeout_sec}'.format(
                call_url=destination,
                exten=extension,
                dialplan=dialplan,
                context=context,
                cid_name=caller_id,
                cid_num=caller_id_number,
                timeout_sec=timeout_sec if timeout_sec else '',
            )
        d = defer.Deferred()
        def success(data):
            d.callback(data)
        def error(failure):
            logger.error(failure.getErrorMessage())
        self.eventsocket.bgapi(
            command).addCallback(success).addErrback(error)
        return d

    def originate_to_app(self, destination, app_name, 
            dialplan='', context='', timeout_sec=0, 
            caller_id='Unknown', caller_id_number='0',
            local_vars={}, export_vars={}, *app_args):
        """
        Originate a new call.

        TODO: document dialplan and context.
        """
        if timeout_sec and not (dialplan and context):
            raise ValueError('Both dialplan and context are required when a '
                'timeout_sec is specified.')
        if context and not dialplan:
            raise ValueError('Dialplan is required when a context '
                'is specified.')
        if local_vars or export_vars:
            if destination.startswith('{'):
                raise ValueError('Destination string already has channel '
                    'variables set. Can not add more.')
            # TODO: handle export_vars properly
            local_vars.update(export_vars)
            var_string = ','.join(
                ['='.join([k, v]) for k, v in local_vars.items()])
            destination = '{%s}%s' % (var_string, destination)
        command = 'originate {call_url} {app_name}({app_args}) ' \
            '{dialplan} {context} {cid_name} {cid_num} {timeout_sec}'.format(
                call_url=destination,
                app_name=application_name,
                app_args=application_args,
                dialplan=dialplan,
                context=context,
                cid_name=caller_id,
                cid_num=caller_id_number,
                timeout_sec=timeout_sec if timeout_sec else '',
            )
        d = defer.Deferred()
        def success(data):
            d.callback(data)
        def error(failure):
            logger.error(failure.getErrorMessage())
        self.eventsocket.bgapi(
            command).addCallback(success).addErrback(error)
        return d

