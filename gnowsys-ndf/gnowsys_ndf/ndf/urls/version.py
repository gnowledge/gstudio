from django.conf.urls import patterns, url

urlpatterns = patterns('gnowsys_ndf.ndf.views.version',
                       url(r'^/(?P<node_id>[\w-]+)/version/(?P<version_no>\d+\.\d+)$', 'version_node', name='node_version'),
                       url(r'^/(?P<node_id>[\w-]+)/version/$', 'version_node', name='node_version'),
                       url(r'^(?P<node_id>[\w-]+)/merge/(?P<version_1>\d+\.\d+)/(?P<version_2>\d+\.\d+)$', 'merge_doc', name='merge_doc'),
                       url(r'^(?P<node_id>[\w-]+)/revert/(?P<version_1>\d+\.\d+)$', 'revert_doc', name='revert_doc'),
                       )
