from django.conf.urls import patterns, url
urlpatterns = patterns('gnowsys_ndf.ndf.views.mailclient',
                       url(r'^[/]$', 'mailclient', name='mailclient'),
                       url(r'^[/]create[/]$', 'mailbox_create_edit', name='mailbox_create_edit'),
                       url(r'^[/]mailresponse[/]','render_mailbox_pane', name='render_mailbox_pane'),
                       url(r'^[/]edit[/](?P<mailboxname>[\w-]+)$', 'mailbox_edit', name='mailbox_edit'),
                       url(r'^[/]delete[/](?P<mailboxname>[\w-]+)$', 'mailbox_delete', name='mailbox_delete'),
                       url(r'^[/]settings[/](?P<mailboxname>[\w-]+)$', 'mailbox_settings', name='mailbox_settings'),
                       # url(r'^[/]error[/]', 'mailclient_error_display', name='mailclient_error_display'),                       
                       )

