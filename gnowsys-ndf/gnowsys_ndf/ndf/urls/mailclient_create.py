from django.conf.urls import patterns, url
urlpatterns = patterns('gnowsys_ndf.ndf.views.mailclient',
                       url(r'^[/]$','mailbox_create_edit', name='mailbox_create_edit'),
                       url(r'^[/]uniqueMailboxName[/]','unique_mailbox_name', name='unique_mailbox_name'),
                       url(r'^[/]uniqueMailboxId[/]','unique_mailbox_id', name='unique_mailbox_id'),
                       )