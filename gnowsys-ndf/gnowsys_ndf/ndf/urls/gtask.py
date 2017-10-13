from django.conf.urls import patterns, url
urlpatterns = patterns('gnowsys_ndf.ndf.views.gtask',
                       url(r'^[/]$', 'gtask', name='gtask'),
                       url(r'^/gcreate$', 'gcreate_edit_task', name='gtask_create_edit'),
                       url(r'^/(?P<task_id>[\w-]+)$', 'task_details', name='task_details'),
                       url(r'^/gedit/(?P<task_id>[\w-]+)/$', 'gcreate_edit_task', name='gtask_edit'),
				       # url(r'^/collection/(?P<task_id>[\w-]+)/page/(?P<each_page>[\w-]+)$', 'task_collection', name='task_collection'),
				       # url(r'^/delete_task/(?P<_id>[\w-]+)$', 'delete_task', name='delete_task'),
				       url(r'^/filter/(?P<choice>[\w-]+)/status/(?P<status>[\w-]+)$','gcheck_filter',name='gcheck_filter'),
				       url(r'^/filter/(?P<choice>[\w-]+)/status/(?P<status>[\w-]+)/page/(?P<each_page>[\w-]+)$','gcheck_filter',name='gfilter'),
				       # url(r'^/task/saveimage$', 'save_image', name='save_image'),
	               
                       )

