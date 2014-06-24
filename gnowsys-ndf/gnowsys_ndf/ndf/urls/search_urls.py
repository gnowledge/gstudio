from django.conf.urls import patterns, include, url

urlpatterns = patterns('gnowsys_ndf.ndf.views.search_views',
    url(r'^home/$', 'search_query', name="search"),
    url(r'^results/$', 'results_search', name="results"),
    url(r'^perform_map_reduce/$','perform_map_reduce',name='perform_map_reduce'),	
)
