from datetime import datetime
from xml.etree.cElementTree import fromstring
from django.db import models


def find_text_safe(element, match):
    """
    Uses the find method on the element to find the match, then returns
    the value of the text attribute on the match, if it exists, or an
    empty string.
    """
    result = element.find(match)
    if result is None:
        return ''
    return result.text

def dt_from_cdr_timestamp(timestamp):
    if not timestamp or timestamp == '0' or len(timestamp) < 11:
        return None
    return datetime.fromtimestamp(
        float('%s.%s' % (timestamp[:10], timestamp[10:])))

def parse_cdr_xml(xml_data):
    parsed = {}
    xml = fromstring(xml_data)
    parsed['uuid'] = find_text_safe(xml, 'variables/uuid')

    parsed['start_dt'] = dt_from_cdr_timestamp(
        find_text_safe(xml, 'callflow/times/created_time'))
    parsed['answered_dt'] = dt_from_cdr_timestamp(
        find_text_safe(xml, 'callflow/times/answered_time'))
    parsed['end_dt'] = dt_from_cdr_timestamp(
        find_text_safe(xml, 'callflow/times/hangup_time'))

    parsed['duration'] = find_text_safe(xml, 'variables/mduration')
    parsed['direction'] = 'IN' if find_text_safe(
        xml, 'variables/direction') == 'inbound' else 'OUT'
    parsed['destination'] = find_text_safe(xml, 
        'callflow/caller_profile/destination_number')
    parsed['originator'] = find_text_safe(xml, 
        'callflow/caller_profile/origination/origination_caller_profile/caller_id_number')

    def originating_channel_test():
        caller_id_name = find_text_safe(xml, 
            'callflow/caller_profile/caller_id_name')
        if caller_id_name == 'Outbound Call' or parsed['direction'] == 'IN':
            return True
        return False
    parsed['is_originating_channel'] = originating_channel_test()

    with open('raw.xml', 'w') as f:
        f.write(xml_data)
    with open('parsed.dict', 'w') as f:
        f.write(str(parsed))
    return xml, parsed


class CallRecord(models.Model):
    freeswitch_server = models.ForeignKey('freeswitch.FreeswitchServer')
    uuid = models.CharField(max_length=36, primary_key=True)
    start_dt = models.DateTimeField()
    answered_dt = models.DateTimeField(null=True, blank=True)
    end_dt = models.DateTimeField(null=True, blank=True)
    duration = models.IntegerField(default=0, 
        help_text="Duration in milliseconds")
    direction = models.CharField(max_length=3,
        choices=(('IN','Inbound'),('OUT','Outbound'),))
    destination = models.CharField(max_length=30)
    destination_extension = models.ForeignKey('freeswitch.SofiaExtension', 
        null=True, blank=True, related_name='cdr_destination_set', 
        help_text="If the destination represents an extension instance, it "
        "will be set here.")
    originator = models.CharField(max_length=30)
    originator_extension = models.ForeignKey('freeswitch.SofiaExtension', 
        null=True, blank=True, related_name='cdr_originator_set', 
        help_text="If the originator represents an extension instance, it "
        "will be set here.")
    is_originating_channel = models.BooleanField()
    cdr_xml = models.TextField()

    class Meta:
        abstract = True
        app_label = 'freeswitch'
        ordering = ('-start_dt',)

    def was_answered(self):
        return bool(self.answered_dt)
    was_answered.boolean = True

    @property
    def duration_seconds(self):
        return float(self.duration) / 1000

