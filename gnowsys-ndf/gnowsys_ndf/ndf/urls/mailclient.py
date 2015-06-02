from django.conf.urls import patterns, url
# from gnowsys_ndf.ndf.views.mailclient import MailView

urlpatterns = patterns('gnowsys_ndf.ndf.views.mailclient',
                       # url(r'^$', MailView.as_view(), name='mailclient'),
                       url(r'^$', 'mailclient', name='mailclient'),
                       url(r'^/create$', 'mailbox_create_edit', name='mailbox_create_edit'),
                       )
