from django.conf.urls import patterns, url

urlpatterns = patterns('gnowsys_ndf.ndf.views.custom_app_view',
			url(r'^[/]$', 'custom_app_view', name='GAPPS'),
			url(r'^/(?P<app_id>[\w-]+)$', 'custom_app_view'),
			url(r'^/(?P<app_id>[\w-]+)/(?P<app_set_id>[\w-]+)$', 'custom_app_view', name='GAPPS_set'),
			url(r'^/(?P<app_id>[\w-]+)/(?P<app_set_id>[\w-]+)/(?P<app_set_instance_id>[\w-]+)$', 'custom_app_view', name='GAPPS_set_instance'),
    			url(r'^/(?P<app_id>[\w-]+)/(?P<app_set_id>[\w-]+)/(?P<app_set_instance_id>[\w-]+)/edit/$', 'custom_app_new_view', name='GAPPS_set_instance_edit'),
    			url(r'^/(?P<app_id>[\w-]+)/(?P<app_set_id>[\w-]+)/new/$', 'custom_app_new_view', name='GAPPS_set_new_instance'),
)
