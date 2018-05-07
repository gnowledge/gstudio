from django.conf.urls import patterns, url

urlpatterns = patterns('gnowsys_ndf.ndf.views.module',

                        # list
                        url(r'^[/]?$', 'list_modules', name='list_modules'),

						# create
                        url(r'^/create/?$', 'module_create_edit', {'cancel_url': 'landing_page'}, name='module_create'),
                        # edit
                        url(r'^/edit/(?P<module_id>[\w-]+)/?$', 'module_create_edit', name='module_edit'),

                        # detail
                        url(r'^/(?P<node_id>[\w-]+)/reorder_units$', 'unit_order_list', name='unit_order_list'),
                        url(r'^/(?P<node_id>[\w-]+)/?$', 'module_detail', name='module_detail'),
                        url(r'^/(?P<node_id>[\w-]+)/(?P<title>[^/]+)/?$', 'module_detail', name='module_detail_url'),

                       )
