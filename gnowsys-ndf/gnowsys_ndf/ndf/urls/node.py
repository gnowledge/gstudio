from django.conf.urls import patterns, url

urlpatterns = patterns('gnowsys_ndf.ndf.views.node',
						# create
                        url(r'^/create/(?P<member_of>[\w-]+)/(?P<detail_url_name>[\w-]+)/?$', 'node_create_edit', {'node_type': 'GSystem', 'node_id': None}, name='node_create'),

						# edit
                        url(r'^/edit/(?P<node_id>[\w-]+)/(?P<detail_url_name>[\w-]+)/?$', 'node_create_edit', name='node_edit'),
	                       )
