from django.db import models
from parseltone.django.apps.freeswitch.models.acl import *
from parseltone.django.apps.freeswitch.models.cdr import *
from parseltone.django.apps.freeswitch.models.event_socket import *
from parseltone.django.apps.freeswitch.models.ivr import *
from parseltone.django.apps.freeswitch.models.sofia import *
from parseltone.django.apps.freeswitch.models.timezones import *


class FreeswitchServer(models.Model):
    serial = models.CharField(max_length=13)

    class Meta:
        app_label = 'freeswitch'

    def __unicode__(self):
        return self.serial
