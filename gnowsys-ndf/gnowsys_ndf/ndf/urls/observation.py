from django.conf.urls import patterns, url

urlpatterns = patterns('gnowsys_ndf.ndf.views.observation',
					url(r'^[/]$', 'all_observations', name='all_observations'),
					url(r'^[/]$', 'all_observations', name='observation'),
					# url(r'^/(?P<app_id>[\w-]+)$', 'all_observations', name='all_observations'),
					url(r'^/(?P<app_id>[\w-]+)/(?P<slug>[-\w]+)/(?P<app_set_id>[^/]+)$', 'observations_app', name='observations_app'),
					url(r'^/(?P<app_id>[\w-]+)/save_observation/(?P<app_set_id>[^/]+)/(?P<slug>[-\w]+)', 'save_observation', name='save_observation'),
					url(r'^/(?P<app_id>[\w-]+)/delete_observation/(?P<app_set_id>[^/]+)/(?P<slug>[-\w]+)', 'delete_observation', name='delete_observation'),
					url(r'^/(?P<app_id>[\w-]+)/save_image/(?P<app_set_id>[^/]+)/(?P<slug>[-\w]+)', 'save_image', name='save_image'),

			  )