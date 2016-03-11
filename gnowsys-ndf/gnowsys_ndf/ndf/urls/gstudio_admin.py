from django.contrib import admin
from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    (r'^data[\/]?', include('gnowsys_ndf.ndf.urls.adminDashboard')),
    (r'^designer[\/]?', include('gnowsys_ndf.ndf.urls.adminDesignerDashboard')),
    url(r'^query-doc/(?P<doc_id_or_name>[^/]+)?$', 'gnowsys_ndf.ndf.views.dev_utils.query_doc'),
)
