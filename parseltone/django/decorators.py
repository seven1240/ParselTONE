from functools import wraps
import logging
from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest
from django.utils.decorators import available_attrs
from django.views.decorators.csrf import csrf_exempt

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


def checkable(view_func):
    def _wrapped_view(request, *args, **kwargs):
        # allows checks for the existence of this view to work
        if request.POST.get('check', False):
            return HttpResponse()
        return view_func(request, *args, **kwargs)
    return wraps(view_func, assigned=available_attrs(view_func))(_wrapped_view)


def POST(view_func):
    @csrf_exempt
    def _wrapped_view(request, *args, **kwargs):
        # bad request if not a POST
        if request.method != 'POST':
            if settings.DEBUG:
                logger.debug('Not accessable via HTTP %s.' % request.method)
            return HttpResponseBadRequest(
                'Not accessable via HTTP %s.' % request.method)
        return view_func(request, *args, **kwargs)
    return wraps(view_func, assigned=available_attrs(view_func))(_wrapped_view)


def POST_keyvalue(key):
    """
    If the key does not exist in the request.POST dictionary, 
    HttpResponseBadRequest will be returned.
    """
    def decorated(view_func):
        @POST
        @csrf_exempt
        def _wrapped_view(request, *args, **kwargs):
            if not request.POST.has_key(key):
                if settings.DEBUG:
                    logger.debug('Key missing: %s' % key)
                return HttpResponseBadRequest('Key missing: %s' % key)
            return view_func(request, *args, **kwargs)
        return wraps(view_func, assigned=available_attrs(view_func))(_wrapped_view)
    return decorated


def POST_keyvalue_matches(key, match_value):
    """
    If the key value from the request.POST dictionary does not match the 
    match_value, HttpResponseBadRequest will be returned.
    
    The match_value may also be a callable that will be passed the value
    and must return False if the value doesn't match.
    """
    def decorated(view_func):
        @POST_keyvalue(key)
        def _wrapped_view(request, *args, **kwargs):
            if request.POST[key] != match_value:
                if callable(match_value) and not match_value(request.POST[key]):
                    if settings.DEBUG:
                        logger.debug('Invalid %s: %s.' % (
                            key, request.POST[key]))
                    return HttpResponseBadRequest(
                        'Invalid %s: %s.' % (key, request.POST[key]))
            return view_func(request, *args, **kwargs)
        return wraps(view_func, assigned=available_attrs(view_func))(_wrapped_view)
    return decorated


def logged_response(condition=True):
    def decorated(view_func):
        def _wrapped_view(request, *args, **kwargs):
            response = view_func(request, *args, **kwargs)
            if callable(condition) and not condition():
                return response
            elif not condition:
                return response
            logger.debug("'{funcname}' view:\n{response}".format(
                funcname=view_func.func_name, response=response
            ))
            return response
        return wraps(view_func, assigned=available_attrs(view_func))(_wrapped_view)
    return decorated

