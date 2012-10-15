from django.db import models
from django.contrib.localflavor.us.forms import USPhoneNumberField
from django.contrib.localflavor.us.forms import phone_digits_re
from django.core.validators import EMPTY_VALUES
from django.utils.encoding import smart_unicode
from django.utils.translation import ugettext_lazy as _
from parseltone.django.apps.freeswitch import validators


class NAPhoneNumberField(models.CharField):
    """
    North American Numbering Plan formatted phone number.
    """
    description = _('Phone number')

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 20
        super(NAPhoneNumberField, self).__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        defaults = {'form_class': USPhoneNumberField}
        defaults.update(kwargs)
        return super(NAPhoneNumberField, self).formfield(**defaults)

    def get_prep_value(self, value):
        return ''.join([c for c in value.split() if c.isdigit()])

    def to_python(self, value):
        if value in EMPTY_VALUES:
            return u''
        value = smart_unicode(value)
        m = phone_digits_re.search(value)
        if m:
            return u'-'.join(m.groups())
        return value


class FSIntegerField(models.CharField):
    """
    A field that will accept FreeSWITCH config file variables, or integers.
    
    Stores as string.
    """
    default_validators = [validators.validate_freeswitch_integer]
    default_error_messages = {
        'invalid': _('This value must be an integer or a FreeSWITCH variable.'),
    }
    description = _("Integer or FreeSWITCH variable")

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = kwargs.get('max_length', 64)
        super(FSIntegerField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        try:
            value = smart_unicode(int(value))
        except (TypeError, ValueError):
            pass
        validators.validate_freeswitch_integer(value)
        return value


class FSIPAddressField(models.CharField):
    """
    Crude field that will accept CIDR network address values or 
    FreeSWITCH config file variables.
    
    Stores as string, so that null can be used.
    """
    default_validators = [validators.validate_freeswitch_ipaddress]
    default_error_messages = {
        'invalid': _('Enter a valid IPv4 address (dot-decimal or CIDR '
            'notation) or a FreeSWITCH variable.'),
    }
    description = _("IPv4 address, in dot-decimal or CIDR notation, or "
        "FreeSWITCH variable")

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = kwargs.get('max_length', 64)
        super(FSIPAddressField, self).__init__(*args, **kwargs)

