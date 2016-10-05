from django.conf.urls import patterns, url

urlpatterns = patterns('gnowsys_ndf.ndf.views.buddy',
			url(r'^[/]$', 'list_buddy', name='list_buddy'),
			url(r'^/update_buddies/$', 'update_buddies', name='update_buddies'),
			url(r'^/search_authors/$', 'search_authors', name='search_authors'),
		)
