from django.conf.urls import patterns, url

urlpatterns = patterns('gnowsys_ndf.ndf.views.module',
                       url(r'^[/]$', 'module', name='module'),
#                       url(r'^(?P<module_id>[\w-]+)$', 'module', name='module'),
		       url(r'^/delete_module/(?P<_id>[\w-]+)$', 'delete_module', name='delete_module'),
                       url(r'^/module_detail/(?P<_id>[\w-]+)$', 'module_detail', name='module_detail'),
                       url(r'^/(?P<_id>[\w-]+)$', 'module_detail', name='module_detail'),
                       )
