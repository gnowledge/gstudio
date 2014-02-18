from django.conf.urls import patterns, url
from gnowsys_ndf.ndf.views import *

urlpatterns = patterns('gnowsys_ndf.ndf.views.module',
                        url(r'^(?P<module_id>[\w-]+)$', 'module', name='module'),
                       )
