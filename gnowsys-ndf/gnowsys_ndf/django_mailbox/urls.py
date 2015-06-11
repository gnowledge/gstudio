from django.conf.urls import patterns, url

urlpatterns = patterns('gnowsys_ndf.ndf.views.mailbox',
    url(r'^$', MailView.as_view(), name='mailbox'),
)