from django.conf.urls import patterns, url

urlpatterns = patterns('gnowsys_ndf.ndf.views.browse_resource',
                       url(r'^(?P<app_id>[\w-]+)$', 'resource_list', name='resource_list')
)