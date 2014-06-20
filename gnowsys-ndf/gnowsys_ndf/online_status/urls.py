from django.conf.urls import patterns, url
#from gnowsys_ndf.online_status.views import gstudio

urlpatterns = patterns('gnowsys_ndf.online_status.views',
    url(r'^test/$', 'test', name="online_users_test"),
    url(r'^example/$', 'example', name="online_users_example"),
    url(r'^$', 'users', name="online_users"),
    url(r'^gstudio/$', 'gstudio'),
)
