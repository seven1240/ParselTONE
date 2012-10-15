from django.conf.urls.defaults import *
from parseltone.django.apps.provisioning import polycom

urls = (patterns('',
    (r'^polycom/', include(polycom.urls)),
), 'provisioning', 'provisioning')
