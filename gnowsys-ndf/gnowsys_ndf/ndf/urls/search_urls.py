from django.conf.urls import patterns, include, url

urlpatterns = patterns('gnowsys_ndf.ndf.views.search_views',
    url(r'^home/$', 'search_query', name="search"),
    url(r'^results/$', 'results_search', name="results"),
    url(r'^perform_map_reduce/$','perform_map_reduce',name='perform_map_reduce'),
    url(r'^advanced_search/$', 'advanced_search', name='advanced_search'),	
    url(r'^advanced_search/results/$', 'advanced_search_results', name='advanced_search_results'),	
    #url(r'^search_group/$', 'search_query_group', name='group_search'),	
    url(r'^group_results/$', 'results_search_group', name="group_results"),
    url(r'^get_attributes/$', 'get_attributes', name='get_attributes'),
    url(r'^get_users/$', 'get_users', name='get_users'),
    url(r'^node_info/(?P<node_name>.+)/$', 'get_node_info', name='get_node_info'),
    url(r'^node_info2/(?P<node_id>[\w-]+)/$', 'get_node_info2', name='get_node_info2'),
)
