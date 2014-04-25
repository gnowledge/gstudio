from django.conf.urls import patterns, url


urlpatterns = patterns('gnowsys_ndf.ndf.views.observations_view',
					url(r'^$', 'all_observations', name='all_observations')
			  )