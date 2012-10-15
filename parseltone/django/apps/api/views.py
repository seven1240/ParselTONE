from functools import wraps
import logging
import urllib
from django.contrib.auth.models import User, Permission
from django.http import HttpResponse, HttpResponseBadRequest
from django.utils.decorators import available_attrs
from parseltone.django.decorators import checkable, POST


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


def username(view_func):
    @POST
    def _wrapped_view(request, *args, **kwargs):
        # must have username key
        username = request.POST.get('username', None)
        if not username:
            return HttpResponseBadRequest('Request requires username '
                'in POST data.')
        # find the user object in the db by username
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return HttpResponseBadRequest('User does not exist.')
        # make sure the user is active
        if not user.is_active:
            return HttpResponseBadRequest('Inactive user.')
        # set a request attribute to refer to this user object
        request.identified_user = user
        return view_func(request, *args, **kwargs)
    return wraps(view_func, assigned=available_attrs(view_func))(_wrapped_view)


def password(view_func):
    """
    Validate request.user with password given in POST data.
    """
    @POST
    @username
    def _wrapped_view(request, *args, **kwargs):
        # got to have the key to the kingdom
        password = request.POST.get('password', None)
        if not password:
            return HttpResponseBadRequest('Request requires password '
                'in POST data.')
        # verify the password
        if not request.identified_user.check_password(password):
            return HttpResponseBadRequest('Invalid password.')
        # set the request.user to this user, overriding AnonymousUser
        request.user = request.identified_user
        del request.identified_user
        return view_func(request, *args, **kwargs)
    return wraps(view_func, assigned=available_attrs(view_func))(_wrapped_view)


@checkable
@password
def login(request):
    return HttpResponse(urllib.urlencode({'success': True}))


@checkable
@username
def permissions(request):
    # get and cleanup the list of requested permissions
    requested_permissions = request.POST.get('permissions', '').split(', ')
    requested_permissions = [x.strip() for x in requested_permissions]
    requested_permissions = [x for x in requested_permissions if x]
    # get list of this users permissions to compare against
    ## if user is superuser, just return all the permission names, 
    ## because user.get_all_permissions() doesn't return anything in 
    ## that case
    if request.identified_user.is_superuser:
        current_permissions = ['%s.%s' % (x.content_type.app_label, 
            x.codename) for x in Permission.objects.all()]
    else:
        current_permissions = request.identified_user.get_all_permissions()
    # construct list of requested permissions which are valid
    permissions = list(set.intersection(
        set(requested_permissions), set(current_permissions)))
    # tx as comma-sep string
    permissions = ', '.join(permissions)
    return HttpResponse(urllib.urlencode({'permissions': permissions}))


