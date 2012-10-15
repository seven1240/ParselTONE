from django.db import models


class Timezone(models.Model):
    name = models.CharField(max_length=255)
    value = models.CharField(max_length=255)

    class Meta:
        app_label = 'freeswitch'

    def __unicode__(self):
        return self.name
