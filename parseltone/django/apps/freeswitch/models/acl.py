from django.core.exceptions import ValidationError
from django.db import models
from parseltone.django.apps.freeswitch import fields


class ACL(models.Model):
    name = models.CharField(max_length=32)
    default = models.CharField(max_length=5, default='deny',
        choices=(('allow', 'Allow'), ('deny', 'Deny')))
    nodes = models.ManyToManyField('freeswitch.ACLNode')

    class Meta:
        app_label = 'freeswitch'
        verbose_name = 'ACL'
        verbose_name_plural = 'ACLs'


class ACLNode(models.Model):
    type = models.CharField(max_length=5, default='allow',
        choices=(('allow', 'Allow'), ('deny', 'Deny')))
    domain = models.CharField(max_length=64, null=True, blank=True)
    cidr = fields.FSIPAddressField(null=True, blank=True,
        help_text="CIDR notation format (ie: 192.168.0.0/24)")
    host = models.IPAddressField(null=True, blank=True,
        help_text="IP address (ie: 192.168.0.0)")
    mask = models.IPAddressField(null=True, blank=True, 
        help_text="Subnet mask in dot-decimal notation format " \
        "(ie: 255.255.255.0)")

    class Meta:
        app_label = 'freeswitch'
        verbose_name = 'ACL Node'
        verbose_name_plural = 'ACL Nodes'

    def __unicode__(self):
        return "({type}) {address}".format(
            type=self.type, 
            address=self.domain or self.cidr or '/'.join([self.host, self.mask]),
        )

    def clean(self):
        if not (self.domain or self.cidr or (self.host and self.mask)):
            raise ValidationError('Must have a domain or CIDR or host/mask.')
        if self.domain and self.cidr:
            raise ValidationError(
                'Domain and CIDR may not be set at the same time.')
        if (self.host or self.mask) and self.cidr:
            raise ValidationError(
                'Host/mask and CIDR may not be set at the same time.')
        if (self.host or self.mask) and self.domain:
            raise ValidationError(
                'Host/mask and domain may not be set at the same time.')

