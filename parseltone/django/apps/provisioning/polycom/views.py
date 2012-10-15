import datetime
import logging
import tempfile
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render_to_response
from django.template import RequestContext
from parseltone.django.apps.freeswitch import models


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


def config(request, phone_model, mac_address):
    try:
        phone = models.SofiaPhone.objects.get(mac_address=mac_address)
    except models.SofiaPhone.DoesNotExist:
        return HttpResponseBadRequest('Invalid device.')
    context = {
        'extensions': phone.sofiaextension_set.all(),
    }
    # update the last_config_date for this phone
    phone.last_config_date = datetime.datetime.now()
    phone.save()
    return render_to_response('provisioning/polycom/config.xml', context,
        context_instance=RequestContext(request))

def zero(request):
    context = {}
    return render_to_response('provisioning/polycom/zero.xml', context,
        context_instance=RequestContext(request))

def put_log(request, mac_address, log_type):
    from pprint import pprint
    path = tempfile.mkstemp()[-1]
    with open(path, 'w') as f:
        f.write(request.raw_post_data)
    logger.info('Written to: %s' % path)
    return HttpResponse()
