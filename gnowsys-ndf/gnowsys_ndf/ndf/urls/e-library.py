from django.conf.urls import patterns, url

urlpatterns = patterns('gnowsys_ndf.ndf.views.e-library',
					   url(r'^[/]$', 'resource_list', name="e-library"),
                       url(r'^/(?P<app_id>[\w-]+)$', 'resource_list', name='resource_list'),
                       url(r'^/details/(?P<_id>[\w-]+)$', 'file_detail', name='resource_detail'),
                       url(r'^/(?P<filetype>[\w-]+)/page-no=(?P<page_no>\d+)/$', 'elib_paged_file_objs', name='elib_paged_file_objs')
)