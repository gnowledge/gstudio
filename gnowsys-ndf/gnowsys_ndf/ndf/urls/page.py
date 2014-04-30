from django.conf.urls import patterns, url

urlpatterns = patterns('gnowsys_ndf.ndf.views.page',
                       url(r'^(?P<app_id>[\w-]+)$', 'page', name='page'),
                       url(r'^create/', 'create_edit_page', name='page_create_edit'),
                       url(r'^details/(?P<app_id>[\w-]+)$', 'page', name='page_details'),
                       url(r'^edit/(?P<node_id>[\w-]+)$', 'create_edit_page', name='page_create_edit'),
                       url(r'^search$', 'page', name='page_search'),
                       url(r'^(?P<node_id>[\w-]+)/translate/$', 'translate_node', name='node_translation'),
                       url(r'^(?P<node_id>[\w-]+)/version/(?P<version_no>\d+\.\d+)$', 'version_node', name='node_version'),
                       url(r'^(?P<node_id>[\w-]+)/merge/(?P<version_1>\d+\.\d+)/(?P<version_2>\d+\.\d+)$', 'merge_doc', name='merge_doc'),
                       url(r'^(?P<node_id>[\w-]+)/revert/(?P<version_1>\d+\.\d+)$', 'revert_doc', name='revert_doc'),
                       url(r'^delete/(?P<node_id>[\w-]+)$', 'delete_page', name='page_delete'),
                       url(r'^page_publish/(?P<node>[\w-]+)$','publish_page',name='publish_page'),
                       
 
                      
)

