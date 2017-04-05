from django.conf.urls import patterns, url

urlpatterns = patterns('gnowsys_ndf.ndf.views.module',

                        # list
                        url(r'^[/]?$', 'list_modules', name='list_modules'),

						# create
                        url(r'^/create/?$', 'module_create_edit', name='module_create_edit'),
                        # edit
                        url(r'^/edit/(?P<module_group_id>[\w-]+)/?$', 'module_create_edit', name='module_edit'),

                        # detail
                        url(r'^/(?P<node_id>[\w-]+)/?$', 'module_detail', name='module_detail'),
                       )
