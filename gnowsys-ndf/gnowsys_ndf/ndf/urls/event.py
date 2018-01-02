from django.conf.urls import patterns, url

urlpatterns = patterns('gnowsys_ndf.ndf.views.event',
    url(r'^[/]$', 'event', name='event'),
    url(r'^/(?P<app_set_id>[\w-]+)$', 'event_detail', name='event_list'),
    url(r'^/create/(?P<app_set_id>[\w-]+)/new/$', 'event_create_edit', name='event_app_instance_create'),
    url(r'^/edit/(?P<app_set_id>[\w-]+)/(?P<app_set_instance_id>[\w-]+)$', 'event_create_edit', name='event_app_instance_edit'),
    url(r'^/(?P<app_set_id>[\w-]+)$', 'event_detail', name='event_app_detail'),      # event_app_detail
    url(r'^/(?P<app_set_id>[\w-]+)/(?P<app_set_instance_id>[\w-]+)$', 'event_detail', name='event_app_instance_detail'),
  )

