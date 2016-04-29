from django.conf.urls import *

urlpatterns = patterns('gnowsys_ndf.ndf.views.type_created',
                       url(r'^$', 'type_created', name='type_created'),
                       url(r'^/default/(?P<node>[^/]+)$', 'default_template', name='basic_temp'),
                       url(r'^/default/(?P<node>[^/]+)/edit/(?P<edit_node>[^/]+)$', 'default_template', name='basic_temp_edit'),
                       url(r'^/graph/(?P<node_id>[^/]+)$', 'adminRenderConceptGraph', name='adminRenderConceptGraph'),
                       url(r'^/graph/(?P<node_id>[^/]+)$', 'adminRenderCollectionGraph', name='adminRenderCollectionGraph'),
                       url(r'^/graph/(?P<node_id>[^/]+)$', 'adminRenderDependencyGraph', name='adminRenderDependencyGraph'),

)