from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('parseltone.django.apps.freeswitch',
    (r'cdr', 'views.cdr'),
    (r'conf/(?P<fs_serial>.*)/$', 'views.conf'),
    (r'directory/(?P<fs_serial>.*)/$', 'views.directory'),
)
