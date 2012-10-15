from django.conf.urls.defaults import *
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/', include(admin.site.urls)),
    (r'^api/', include('parseltone.django.apps.api.urls')),
    (r'^freeswitch/', include('parseltone.django.apps.freeswitch.urls')),
)
