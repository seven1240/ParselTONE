from functools import wraps
import logging
from django.conf import settings
from django.http import HttpResponseBadRequest
from django.utils.decorators import available_attrs
from parseltone.django.apps.freeswitch import models

logger = logging.getLogger(__name__)


def fs_serial(view_func):
    """
    Makes the view require a keyword argument 'fs_serial' and sets
    request.freeswitch to the model instance from freeswitch.FreeswitchServer.
    """
    def _wrapped_view(request, *args, **kwargs):
        if not kwargs.has_key('fs_serial'):
            if settings.DEBUG:
                logger.debug("Missing required parameter 'fs_serial'.")
            return HttpResponseBadRequest(
                "Missing required parameter 'fs_serial'.")
        fs_serial = kwargs.pop('fs_serial')
        try:
            request.freeswitch = models.FreeswitchServer.objects.get(
                serial=fs_serial)
        except models.FreeswitchServer.DoesNotExist:
            if settings.DEBUG:
                logger.debug("Invalid serial number: %s" % fs_serial)
            return HttpResponseBadRequest(
                "Invalid serial number: %s" % fs_serial)
        return view_func(request, *args, **kwargs)
    return wraps(view_func, assigned=available_attrs(view_func))(_wrapped_view)
