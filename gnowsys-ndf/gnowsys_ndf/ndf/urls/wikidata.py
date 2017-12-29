from django.conf.urls import patterns, url

urlpatterns = patterns('gnowsys_ndf.ndf.views.wikidata',
                        url(r'^[/]$', 'index', name='wikidata_main'),
                        url(r'^[/]$', 'index', name='wikidata'),
			url(r'^/details/(?P<topic_id>[\w-]+)$', 'details', name = 'wikidata_topic_display'),
			url(r'^/details/(?P<topic_id>[\w-]+)/tag/(?P<tag>[^/]+)$', 'tag_view_list', name = 'tag_topic_display'),
			

)
