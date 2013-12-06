from django.conf.urls import patterns, url

from django.views.generic import TemplateView

from gnowsys_ndf.ndf.views import *


urlpatterns = patterns('gnowsys_ndf.ndf.views.page',
                        url(r'^(?P<app_id>[\w-]+)$', 'page', name='page'),
                        url(r'^create_page/', 'create_page', name='create_page'),
                        url(r'^(?P<node_id>[\w-]+)/edit$', 'edit_page', name='edit_page'),
)

