from django.conf.urls import patterns, url
from gnowsys_ndf.ndf.views.group import GroupCreateEditHandler,EventGroupCreateEditHandler
from django.views.generic import TemplateView

urlpatterns = patterns('gnowsys_ndf.ndf.views.group',
                        url(r'^[/]$', 'group', name='group'),
                        url(r'^/(?P<app_id>[\w-]+)$', 'group', name='group'),
                        url(r'^/create_group/', GroupCreateEditHandler.as_view(), {'action': 'create'}, name='create_group'),
                        url(r'^/edit_group/', GroupCreateEditHandler.as_view(), {'action': 'edit'}, name='edit_group'),
                        url(r'^/create_event/(?P<sg_type>[^/]+)/$', EventGroupCreateEditHandler.as_view(), {'action': 'create'}, name='create_event_group'),
                        url(r'^/edit_event/(?P<sg_type>[^/]+)/$', EventGroupCreateEditHandler.as_view(), {'action': 'edit'}, name='edit_event_group'),
                        url(r'^/group_publish/(?P<node>[\w-]+)$', 'publish_group', name='publish_group'),
                        url(r'^/switch_group/(?P<node_id>[\w-]+)$', 'switch_group', name='switch_group'),
                        url(r'^/cross_publish/$', 'cross_publish', name='cross_publish'),
                        url(r'^/app_selection/', 'app_selection', name='app_selection'),
                        url(r'^/create_sub_group/', 'create_sub_group', name='create_sub_group'),
                        url(r'^/upload_using_save_file/', 'upload_using_save_file', name='upload_using_save_file'),
                        #url(r'^/(?P<groups_category>[\w-]+)/nroer_groups/?$', 'nroer_groups', name='nroer_groups'),
                        url(r'^/(?P<app_id>[\w-]+)/value/(?P<agency_type>[\w-]+)/?$', 'group', name='groups_by_agency_type'),
                        url(r'^/notification/details','notification_details' , name='notification_details'),
                    )

urlpatterns += patterns('gnowsys_ndf.ndf.views.ajax_views',
                        url(r'^/check_group/', 'checkgroup', name='check_group'),
                    )

urlpatterns += patterns('gnowsys_ndf.ndf.views.notify',
                        url(r'^/notify/join/$', 'notifyuser', name='notifyuser'),
                        url(r'^/notify/remove/$', 'notify_remove_user', name='notifyremuser'),
                        url(r'^/notify/invite_users/$', 'invite_users', name='sendinvitation'),
                        url(r'^/notify/invite_admins/$', 'invite_admins', name='admininvitations'),
                    )
