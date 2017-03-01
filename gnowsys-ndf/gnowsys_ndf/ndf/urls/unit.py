from django.conf.urls import patterns, url

urlpatterns = patterns('gnowsys_ndf.ndf.views.unit',
                        # listing
                        url(r'^[/]?$', 'list_unit', name='list_units'),
                        # create
                        url(r'^/create/?$', 'list_unit', name='list_units'),
                        # detail and edit
                        url(r'^[/](?P<_id>[\w-]+)/?$', 'list_unit', name='list_units'),
)
