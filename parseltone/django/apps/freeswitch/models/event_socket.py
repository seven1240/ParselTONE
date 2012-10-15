from django.db import models
from parseltone.django.apps.freeswitch import fields


class EventSocket(models.Model):
    freeswitch_server = models.ForeignKey('freeswitch.FreeswitchServer')
    nat_map = models.BooleanField()
    listen_ip = fields.FSIPAddressField(default='$${local_ip_v4}')
    listen_port = models.IntegerField(default=8021)
    password = models.CharField(max_length=64)
    apply_inbound_acl = models.ForeignKey('freeswitch.ACL', 
        null=True, blank=True)

    class Meta:
        app_label = 'freeswitch'

    def __unicode__(self):
        return ':'.join([self.listen_ip, str(self.listen_port)])

