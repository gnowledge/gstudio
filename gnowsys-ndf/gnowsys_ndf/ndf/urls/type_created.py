from django.conf.urls import *

urlpatterns = patterns('gnowsys_ndf.ndf.views.type_created',
                       url(r'^$', 'type_created', name='type_created'),
                       url(r'^/default/(?P<node>[^/]+)$', 'default_template', name='basic_temp'),
)