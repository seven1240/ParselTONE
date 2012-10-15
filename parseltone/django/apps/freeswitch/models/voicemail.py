from django.db import models


class Messages(models.Model):
    created_epoch = models.IntegerField(null=True, blank=True)
    read_epoch = models.IntegerField(null=True, blank=True)
    username = models.CharField(max_length=255, blank=True)
    domain = models.CharField(max_length=255, blank=True)
    uuid = models.CharField(max_length=255, blank=True)
    cid_name = models.CharField(max_length=255, blank=True)
    cid_number = models.CharField(max_length=255, blank=True)
    in_folder = models.CharField(max_length=255, blank=True)
    file_path = models.CharField(max_length=255, blank=True)
    message_len = models.IntegerField(null=True, blank=True)
    flags = models.CharField(max_length=255, blank=True)
    read_flags = models.CharField(max_length=255, blank=True)
    forwarded_by = models.CharField(max_length=255, blank=True)

    class Meta:
        db_table = u'voicemail_msgs'


class Preferences(models.Model):
    username = models.CharField(max_length=255, blank=True)
    domain = models.CharField(max_length=255, blank=True)
    name_path = models.CharField(max_length=255, blank=True)
    greeting_path = models.CharField(max_length=255, blank=True)
    password = models.CharField(max_length=255, blank=True)

    class Meta:
        db_table = u'voicemail_prefs'
