from django.conf.urls import patterns, url

from gnowsys_ndf.ndf.views import mailbox

urlpatterns = patterns('',
    url(r'^$', views.IndexView.as_view(), name='index'),
)