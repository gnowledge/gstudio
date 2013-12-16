from django.conf.urls import patterns, url

from django.views.generic import TemplateView

from gnowsys_ndf.ndf.views import *


urlpatterns = patterns('gnowsys_ndf.ndf.views.page',
                        url(r'^(?P<app_id>[\w-]+)/list$', 'page', name='page'),
                        url(r'^create_page/', 'create_page', name='create_page'),
                        url(r'^/detail/(?P<node_id>[\w-]+)$', 'edit_page', name='edit_page'),
                        url(r'^version/(?P<node_id>[\w-]+)/(?P<version_no>\d+\.\d+)$', 'version_page', name='version_page'),
)

