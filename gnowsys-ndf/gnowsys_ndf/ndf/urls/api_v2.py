from django.conf.urls import patterns, url

urlpatterns = patterns('gnowsys_ndf.ndf.views.api_v2',
                        # GET: api/v2/<group>/<resource>/<user>/
                        url(r'^/?$', 'api_get_gs_nodes'),
                        url(r'^/schema/?$', 'db_schema'),
                        url(r'^/schema/(?P<collection_name>[^/]+)?$', 'db_schema'),
                        url(r'^/schema/(?P<collection_name>[^/]+)/(?P<field_name>[^/]+)?$', 'db_schema'),
                        url(r'^/schema/(?P<collection_name>[^/]+)/(?P<field_name>[^/]+)/(?P<field_value>[^/]+)?$', 'db_schema'),
                        url(r'^/(?P<field_name>[^/]+)/?$', 'api_get_field_values'),
                        # url(r'^/create/?$', 'api_create_gs'),
                        url(r'^/create/(?P<gst_name>[^/]+)/?$', 'api_create_gs'),
)
