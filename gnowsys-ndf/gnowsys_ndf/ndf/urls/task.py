from django.conf.urls import patterns, url
urlpatterns = patterns('gnowsys_ndf.ndf.views.task',
                       url(r'^[/]$', 'task', name='task'),
                       url(r'^/create$', 'create_edit_task', name='task_create_edit'),
                       url(r'^/(?P<task_id>[\w-]+)$', 'task_details', name='task_details'),
                       url(r'^/edit/(?P<task_id>[\w-]+)/$', 'create_edit_task', name='task_edit'),
		       url(r'^/collection/(?P<task_id>[\w-]+)/page/(?P<each_page>[\w-]+)$', 'task_collection', name='task_collection'),
		       url(r'^/delete_task/(?P<_id>[\w-]+)$', 'delete_task', name='delete_task'),
		       url(r'^/filter/(?P<choice>[\w-]+)/status/(?P<status>[\w-]+)$','check_filter',name='check_filter'),
		       url(r'^/filter/(?P<choice>[\w-]+)/status/(?P<status>[\w-]+)/page/(?P<each_page>[\w-]+)$','check_filter',name='filter'),
		       url(r'^/task/saveimage$', 'save_image', name='save_image'),
	               
                       )

