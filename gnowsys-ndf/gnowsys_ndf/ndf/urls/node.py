from django.conf.urls import patterns, url

urlpatterns = patterns('gnowsys_ndf.ndf.views.node',
						# create / edit
                        url(r'^/create/(?P<member_of>[\w-]+)/(?P<detail_url_name>[\w-]+)/?$', 'node_create_edit', {'node_type': 'GSystem', 'node_id': None}, name='node_create'),

                        url(r'^/edit/?$', 'node_create_edit', {'node_id': None, 'detail_url_name': None}, name='node_edit'),
                       )
