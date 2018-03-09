from django.conf.urls import patterns, url

urlpatterns = patterns('gnowsys_ndf.ndf.views.dev_utils',
		#url(r'^/template[/]$', 'render_test_template', name='render_test_template'),
		#url(r'^/template/(?P<group_id>[\w-]+)/(?P<filetype>[\w-]+)/page-no=(?P<page_no>\d+)/$', 'elib_paged_file_objects', name='elib_paged_file_objects'),
		#url(r'^/template/(?P<app_id>[\w-]+)$', 'render_test_template', name='resource_list'),
		url(r'^git/branch/?$', 'git_branch', name='git_branch'),
		url(r'^git/(?P<git_command>[\w-]+)$', 'git_misc', name='git_misc'),
)

urlpatterns += patterns('',
	    url(r'^/query/(?P<doc_id_or_name>[^/]+)?$', 'gnowsys_ndf.ndf.views.dev_utils.query_doc'),
	    url(r'^/query/(?P<doc_id_or_name>[\w-]+)/(?P<option>[^/]+)?$', 'gnowsys_ndf.ndf.views.dev_utils.query_doc'),
)
