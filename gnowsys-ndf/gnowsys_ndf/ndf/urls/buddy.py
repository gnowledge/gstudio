from django.conf.urls import patterns, url

urlpatterns = patterns('gnowsys_ndf.ndf.views.buddy',
			url(r'^[/]$', 'list_buddy', name='list_buddy'),
		)
