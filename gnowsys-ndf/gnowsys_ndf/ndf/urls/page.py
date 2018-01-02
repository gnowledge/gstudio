from django.conf.urls import patterns, url

urlpatterns = patterns('gnowsys_ndf.ndf.views.page',
                       url(r'^[/]$', 'page', name='page'),
                       url(r'^/page_info/page-no=(?P<page_no>\d+)/$', 'page', name='page_paged'),
                       # url(r'^/page_collections/page-no=(?P<page_no>\d+)/$', 'page_collection', name='page_collections_paged'),
                       url(r'^/details/(?P<app_id>[\w-]+)$', 'page', name='page_details'),
                       url(r'^/(?P<app_id>[\w-]+)$', 'page', name='page_details'),
                       url(r'^/create/', 'create_edit_page', name='page_create_edit'),
                       url(r'^/edit/(?P<node_id>[\w-]+)$', 'create_edit_page', name='page_create_edit'),
                       url(r'^/search$', 'page', name='page_search'),
                       url(r'^/(?P<node_id>[\w-]+)/translate/$', 'translate_node', name='node_translation'),
                       url(r'^/page_publish/(?P<node>[\w-]+)$','publish_page',name='publish_page'),
                       url(r'^/delete/(?P<node_id>[\w-]+)$', 'delete_page', name='page_delete'),
                      
)

