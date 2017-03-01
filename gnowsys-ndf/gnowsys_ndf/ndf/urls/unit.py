from django.conf.urls import patterns, url

urlpatterns = patterns('gnowsys_ndf.ndf.views.unit',
                        # list
                        url(r'^[/]?$', 'list_units', name='list_units'),
                        # create
                        url(r'^/create/?$', 'unit_create_edit', name='unit_create_edit'),
                        # detail
                        url(r'^[/](?P<_id>[\w-]+)/?$', 'unit_detail', name='unit_detail'),
)
