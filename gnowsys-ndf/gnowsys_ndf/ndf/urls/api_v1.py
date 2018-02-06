from django.conf.urls import patterns, url

urlpatterns = patterns('gnowsys_ndf.ndf.views.api_v1',
                        # GET: api/v1/<group_id>/<files>/<nroer_team>/
                        url(r'^/?$', 'api_get_gs_nodes'),
                        url(r'^/(?P<field_name>[^/]+)/?$', 'api_get_field_values'),
                        # url(r'^/(?P<group_name_or_id>[^/]+)/(?P<gst_name_or_id>[^/]+)/?$', 'api_get_group_gst_nodes', name='(?P<unit_group_id>[\w-]+)'),
                        # url(r'^/(?P<group_name_or_id>[^/]+)/(?P<gst_name_or_id>[^/]+)/(?P<username_or_id>[^/]+)/?$', 'api_get_group_gst_nodes', name='(?P<unit_group_id>[\w-]+)'),
)


