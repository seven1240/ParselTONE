import os
from django.conf.urls.defaults import *
from django.views import static

urls = (patterns('parseltone.django.apps.provisioning.polycom.views',
    url(r'^[0]{12}.cfg', 'zero', name='zero'),
    url(r'^config/(?P<phone_model>.*)/(?P<mac_address>.*).cfg', 'config', name='config'),
    url(r'^(?P<mac_address>.*)-(?P<log_type>.*).log', 'put_log', name='put_log'),
    url(r'^(?P<path>.*)', static.serve, {
        'document_root': os.path.join(os.path.dirname(__file__), 'static'),
    }),
), 'polycom', 'polycom')
