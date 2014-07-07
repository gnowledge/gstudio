from django.conf.urls import patterns, url

urlpatterns = patterns('gnowsys_ndf.ndf.views.meeting',
                       url(r'^$', 'meeting', name='meeting'),
                       url(r'^/create$', 'create_edit_meeting', name='meeting_create_edit'),
                       url(r'^/(?P<meeting_id>[\w-]+)/$', 'meeting_details', name='meeting_details'),
                       url(r'^/edit/(?P<meeting_id>[\w-]+)/$', 'create_edit_meeting', name='meeting_edit'),
		       url(r'^/delete_meeting/(?P<_id>[\w-]+)$', 'delete_meeting', name='delete_meeting'),
                       )
