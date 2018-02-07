from django.conf.urls import patterns, url

urlpatterns = patterns('gnowsys_ndf.ndf.views.dev_utils',
		url(r'^template/$', 'render_test_template', name='render_test_template'),
		
		url(r'^git/branch/?$', 'git_branch', name='git_branch'),
		url(r'^git/(?P<git_command>[\w-]+)$', 'git_misc', name='git_misc'),
)

urlpatterns += patterns('',
	    url(r'^query/(?P<doc_id_or_name>[^/]+)?$', 'gnowsys_ndf.ndf.views.dev_utils.query_doc'),
	    url(r'^query/(?P<doc_id_or_name>[\w-]+)/(?P<option>[^/]+)?$', 'gnowsys_ndf.ndf.views.dev_utils.query_doc'),
)
