from django.conf.urls import patterns, url

urlpatterns = patterns('gnowsys_ndf.ndf.views.trash',
				url(r'^/delete/(?P<node_id>[\w-]+)$', 'trash_resource',name='trash_resource'),
				url(r'^/delete_group$', 'delete_group',name='delete_group'),
				url(r'^/delete_group/(?P<url_name>[\w-]+)?$', 'delete_group',name='delete_group_url_redirect'),
				url(r'^/delete$', 'delete_resource',name='delete_resource'),
				url(r'^/restore$', 'restore_resource',name='restore_resource'),
				url(r'^/delete_multiple_resources', 'delete_multiple_resources', name='delete_multiple_resources'),
		 	)


