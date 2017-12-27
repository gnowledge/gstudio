from django.conf.urls import patterns, include, url
urlpatterns = patterns('gnowsys_ndf.ndf.views.mailclient',
                       url(r'^[/]$', 'mailclient', name='mailclient'),
                       url(r'^[/]error[/](?P<error_obj>[\w-]+)$', 'mailclient_error_display', name='mailclient_error_display'),
                       url(r'^[/]create', include('gnowsys_ndf.ndf.urls.mailclient_create')),
                       url(r'^[/]mailresponse[/]','render_mailbox_pane', name='render_mailbox_pane'),
                       url(r'^[/]edit[/](?P<mailboxname>[\w-]+)$', 'mailbox_edit', name='mailbox_edit'),
                       url(r'^[/]delete[/](?P<mailboxname>[\w-]+)$', 'mailbox_delete', name='mailbox_delete'),
                       url(r'^[/]settings[/](?P<mailboxname>[\w-]+)$', 'mailbox_settings', name='mailbox_settings'),
                       url(r'^[/]edit/uniqueMailboxId/','unique_mailbox_id', name='unique_mailbox_id'),
                       url(r'^[/]edit/uniqueMailboxName/','unique_mailbox_name', name='unique_mailbox_id'),
                       url(r'^[/]new_mail[/](?P<mailboxname>[\w-]+)[/]$', 'compose_mail', name='compose_mail'),
                       url(r'^[/]mailstatuschange[/]','update_mail_status', name='update_mail_status'),
                       url(r'^[/]mail_body[/]','fetch_mail_body', name='fetch_mail_body'),
                       url(r'^[/]uniqueMailboxName/[/]','unique_mailbox_name', name='unique_mailbox_name'),
                       url(r'^[/]uniqueMailboxId/[/]','unique_mailbox_id', name='unique_mailbox_id'),
                       # url(r'^[/]error[/]', 'mailclient_error_display', name='mailclient_error_display'),                       
                       )

