from django.conf.urls import patterns, url
from gnowsys_ndf.online_status.views import gstudio

urlpatterns = patterns('',
    url(r'^test/$', 'online_status.views.test', name="online_users_test"),
    url(r'^example/$', 'online_status.views.example', name="online_users_example"),
    url(r'^$', 'online_status.views.users', name="online_users"),
    url(r'^gstudio/$', gstudio),
)
