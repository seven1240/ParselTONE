import logging
from django.conf import settings
from django.shortcuts import render_to_response
from django.template import RequestContext
from parseltone.django.apps.freeswitch import models
from parseltone.django.decorators import POST
from parseltone.django.decorators import POST_keyvalue_matches
from parseltone.django.decorators import POST_keyvalue
from parseltone.django.decorators import logged_response
from parseltone.django.apps.freeswitch.decorators import fs_serial


logger = logging.getLogger(__name__)

#########
# http://djangosnippets.org/snippets/1654/
# print exceptions to console
# (modified slightly to use python logging instead of print)
import sys
from django.core.signals import got_request_exception

def exception_printer(sender, **kwargs):
    logger.exception(sys.exc_info()[1])

got_request_exception.connect(exception_printer)
############


@POST
def cdr(request):
    logging.debug(request.POST)
    record = models.CallRecord.objects.create(cdr_data=request.POST)
    return render_to_response('freeswitch/not_found.xml')


@logged_response()
@fs_serial
@POST_keyvalue_matches('section', 'configuration')
def conf(request):
    conf_name = request.POST['key_value']
    context_func = globals().get('conf_%s' % conf_name.split('.')[0])
    if not callable(context_func):
        if settings.DEBUG:
            logger.debug('Config file %s requested, but not found.' % conf_name)
        return render_to_response('freeswitch/not_found.xml',
            {'note': conf_name})
    try:
        context = context_func(request)
    except Exception, e:
        logger.exception(e)
        return render_to_response('freeswitch/not_found.xml',
            {'note': '{}: {}'.format(conf_name, str(e))})
    context.update({'conf_name': conf_name})
    return render_to_response('freeswitch/confs/%s.xml' % conf_name,
        context, context_instance=RequestContext(request))

def conf_acl(request):
    return {
        'acls': models.ACL.objects.all(),
    }

def conf_cdr(request):
    return {}

def conf_ivr(request):
    return {
        'menus': models.IVRMenu.objects.all(),
    }

def conf_sofia(request):
    return {
        'global_settings': models.SofiaGlobalSettings.objects.get(
            freeswitch_server=request.freeswitch),
        'profiles': models.SofiaProfile.objects.filter(
            freeswitch_server=request.freeswitch),
    }

def conf_event_socket(request):
    return {
        'event_socket': models.EventSocket.objects.get(
            freeswitch_server=request.freeswitch),
    }

def conf_timezones(request):
    return {
        'timezones': models.Timezone.objects.all(),
    }


@fs_serial
@POST_keyvalue_matches('section', 'directory')
@POST_keyvalue('action')
def directory(request, context={}):
    action = request.POST['action']
    notfound_response = render_to_response('freeswitch/not_found.xml',
            {'note': 'directory action: %s' % action})

    action_func = globals().get('directory_%s' % action.replace('-', '_'))
    if not callable(action_func):
        if settings.DEBUG:
            logger.debug('Directory for action %r is unsupported.' % action)
        return notfound_response

    context.update({
        'action': action,
        'hostname': request.POST['hostname'],
        'tag_name': request.POST['tag_name'],
        'key_name': request.POST['key_name'],
        'key_value': request.POST['key_value'],
        'key': request.POST['key'],
        'user': request.POST['user'],
        'domain': request.POST['domain'],
    })
    return action_func(request, notfound_response, context=context)

@logged_response()
def directory_sip_auth(request, notfound_response, context={}):
    action = context['action']
    tag_name = context['tag_name']
    key_name = context['key_name']
    key_value = context['key_value']
    key = context['key']
    domain = context['domain']
    user = context['user']
    # at this time, unsure what other values might be in the key_name,
    ## but we want to make sure the tag_name and key_name are 'domain'
    ## and 'name', respectively
    if tag_name != 'domain' and key_name != 'name':
        if settings.DEBUG:
            logger.debug('Directory (%r): tag_name %r with '
                'key_name %r are unsupported.' % (
                    action, tag_name, key_name))
        return notfound_response
    # the domain and the key_value must match
    if domain != key_value:
        if settings.DEBUG:
            logger.debug('Directory (%r): domain and key_value '
                'do not match.' % action)
        return notfound_response
    # we only support lookups when the 'key' is set to 'id'
    if key != 'id':
        if settings.DEBUG:
            logger.debug("Directory (%r): Extension lookup via %r "
                "is unsupported." % (action, key))
        return notfound_response
    # find the extension by id and domain
    try:
        context.update({'extension': models.SofiaExtension.objects.get(
            register_username=user, sofia_profile__domain__address=domain)})
    except models.SofiaExtension.DoesNotExist:
        if settings.DEBUG:
            logger.debug("Directory (%r): SofiaExtension %r does not "
                "exist at domain %r." % (action, user, domain))
        return notfound_response
    return render_to_response('freeswitch/directory.xml', context,
        context_instance=RequestContext(request))

def directory_message_count(request, notfound_response, context={}):
    return directory_sip_auth(request, notfound_response, context=context)
