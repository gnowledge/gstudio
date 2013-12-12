from django.conf.urls import patterns, url

from django.views.generic import TemplateView

from gnowsys_ndf.ndf.views import *


urlpatterns = patterns('gnowsys_ndf.ndf.views.page',
                        url(r'^(?P<app_id>[\w-]+)/list$', 'page', name='page'),
                        url(r'^create/', 'create_page', name='page-create'),
                        url(r'^(?P<node_id>[\w-]+)/detail$', 'edit_page', name='page-detail'),
                        url(r'^(?P<node_id>[\w-]+)/edit$', 'edit_page', name='page-edit'),
                        url(r'^version-page/(?P<node_id>[\w-]+)/(?P<version_no>\d+\.\d+)$', 'version_page', name='version_page'),
)

