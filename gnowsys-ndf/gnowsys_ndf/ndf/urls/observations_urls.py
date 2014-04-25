from django.conf.urls import patterns, url


urlpatterns = patterns('gnowsys_ndf.ndf.views.observations_view',
					url(r'^/(?P<app_set_id>[^/]+)/(?P<slug>[-\w]+)$', 'observations_app', name='observations_app'),
					url(r'^$', 'all_observations', name='all_observations')

			  )